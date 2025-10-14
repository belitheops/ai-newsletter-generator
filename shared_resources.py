"""
Shared resources module for the newsletter generator.

This module contains shared resources that need to persist across Streamlit reruns,
such as threading locks for coordinating newsletter generation.
"""

import threading

# Global lock for newsletter generation to prevent concurrent runs
# This lock is shared between manual triggers (via Streamlit) and scheduled runs
newsletter_generation_lock = threading.Lock()
