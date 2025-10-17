#!/usr/bin/env python3
"""
Script to create a GitHub repository and push code using Replit GitHub connector
"""

import os
import requests
from github import Github
import subprocess
import sys

def get_github_token():
    """Get GitHub access token from Replit connector"""
    try:
        hostname = os.getenv('REPLIT_CONNECTORS_HOSTNAME')
        repl_identity = os.getenv('REPL_IDENTITY')
        web_repl_renewal = os.getenv('WEB_REPL_RENEWAL')
        
        # Determine X_REPLIT_TOKEN
        x_replit_token = None
        if repl_identity:
            x_replit_token = f'repl {repl_identity}'
        elif web_repl_renewal:
            x_replit_token = f'depl {web_repl_renewal}'
        
        if not hostname or not x_replit_token:
            raise Exception("Replit connector environment not found")
        
        # Fetch connection settings
        url = f'https://{hostname}/api/v2/connection?include_secrets=true&connector_names=github'
        headers = {
            'Accept': 'application/json',
            'X_REPLIT_TOKEN': x_replit_token
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            if items and len(items) > 0:
                settings = items[0].get('settings', {})
                # Try both possible token locations
                token = settings.get('access_token') or settings.get('oauth', {}).get('credentials', {}).get('access_token')
                if token:
                    print("✅ GitHub token retrieved from Replit connector")
                    return token
        
        raise Exception(f"Failed to get GitHub token: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Error getting GitHub token: {e}")
        return None

def create_repository(token, repo_name, description, private=False):
    """Create a new GitHub repository"""
    try:
        g = Github(token)
        user = g.get_user()
        
        print(f"📝 Creating repository '{repo_name}' for user: {user.login}")
        
        # Check if repo already exists
        try:
            existing_repo = user.get_repo(repo_name)
            print(f"⚠️  Repository '{repo_name}' already exists at: {existing_repo.html_url}")
            return existing_repo
        except:
            pass  # Repo doesn't exist, continue creating
        
        # Create the repository
        repo = user.create_repo(
            name=repo_name,
            description=description,
            private=private,
            auto_init=False  # We'll push our own code
        )
        
        print(f"✅ Repository created successfully!")
        print(f"🔗 URL: {repo.html_url}")
        return repo
        
    except Exception as e:
        print(f"❌ Error creating repository: {e}")
        return None

def run_command(cmd, cwd=None):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def setup_git_and_push(repo_url, token):
    """Initialize git, commit, and push to GitHub"""
    try:
        # Configure git user if not set
        print("\n📋 Configuring git...")
        run_command('git config user.email "noreply@replit.com"')
        run_command('git config user.name "Replit User"')
        
        # Check if already a git repo
        success, _ = run_command('git rev-parse --git-dir')
        
        if not success:
            print("🔧 Initializing git repository...")
            run_command('git init')
        else:
            print("✅ Git repository already initialized")
        
        # Add all files
        print("📦 Adding files to git...")
        run_command('git add .')
        
        # Commit
        print("💾 Creating commit...")
        success, output = run_command('git commit -m "Initial commit: AI Daily Newsletter Generator"')
        if not success and "nothing to commit" in output:
            print("ℹ️  No changes to commit")
        elif success:
            print("✅ Commit created")
        
        # Add remote with token authentication
        print("🔗 Adding remote repository...")
        # Remove existing origin if it exists
        run_command('git remote remove origin')
        
        # Parse repo URL to insert token
        # Format: https://github.com/user/repo.git
        # Need: https://token@github.com/user/repo.git
        if repo_url.startswith('https://github.com/'):
            auth_url = repo_url.replace('https://github.com/', f'https://{token}@github.com/')
            run_command(f'git remote add origin {auth_url}')
            print("✅ Remote added")
        else:
            print(f"❌ Unexpected repo URL format: {repo_url}")
            return False
        
        # Get current branch name
        success, branch = run_command('git rev-parse --abbrev-ref HEAD')
        if success:
            branch = branch.strip()
        else:
            branch = 'main'
        
        # Rename to main if needed
        if branch != 'main':
            run_command('git branch -M main')
            branch = 'main'
        
        # Push to GitHub
        print(f"🚀 Pushing to GitHub (branch: {branch})...")
        success, output = run_command(f'git push -u origin {branch}')
        
        if success:
            print("✅ Code pushed to GitHub successfully!")
            return True
        else:
            # Try force push if there's a conflict
            print("⚠️  Initial push failed, trying force push...")
            success, output = run_command(f'git push -u origin {branch} --force')
            if success:
                print("✅ Code pushed to GitHub successfully (force)!")
                return True
            else:
                print(f"❌ Push failed: {output}")
                return False
        
    except Exception as e:
        print(f"❌ Error setting up git and pushing: {e}")
        return False

def main():
    print("=" * 60)
    print("  🚀 GitHub Repository Creator")
    print("=" * 60)
    print()
    
    # Configuration
    REPO_NAME = "ai-newsletter-generator"
    DESCRIPTION = "Automated AI newsletter system with RSS scraping, deduplication, AI summarization, and email distribution"
    PRIVATE = False  # Set to True for private repo
    
    # Step 1: Get GitHub token
    print("Step 1: Getting GitHub access token...")
    token = get_github_token()
    if not token:
        print("\n❌ Failed to get GitHub token. Please ensure GitHub integration is set up.")
        sys.exit(1)
    
    # Step 2: Create repository
    print(f"\nStep 2: Creating repository '{REPO_NAME}'...")
    repo = create_repository(token, REPO_NAME, DESCRIPTION, PRIVATE)
    if not repo:
        print("\n❌ Failed to create repository.")
        sys.exit(1)
    
    # Step 3: Push code
    print("\nStep 3: Setting up git and pushing code...")
    success = setup_git_and_push(repo.clone_url, token)
    
    if success:
        print("\n" + "=" * 60)
        print("  ✅ SUCCESS!")
        print("=" * 60)
        print(f"\n🎉 Your code is now on GitHub!")
        print(f"🔗 Repository URL: {repo.html_url}")
        print(f"📋 Clone URL: {repo.clone_url}")
        print("\n" + "=" * 60)
    else:
        print("\n" + "=" * 60)
        print("  ⚠️  PARTIAL SUCCESS")
        print("=" * 60)
        print(f"\n✅ Repository created: {repo.html_url}")
        print("❌ But code push failed. You can manually push using:")
        print(f"   git remote add origin {repo.clone_url}")
        print(f"   git push -u origin main")
        print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
