/**
 * PULSE SOCIAL - FRONTEND CORE JAVASCRIPT
 * Dynamic single-page-like interactions, real-time counters, modals, toasts, theme toggler
 */

// Helper to get CSRF cookie for Django POST requests
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Toast Notification System
function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  let icon = '✨';
  if (type === 'success') icon = '✅';
  if (type === 'error') icon = '⚠️';

  toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = 'toastOut 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Dark / Light Theme Toggle
function initThemeToggle() {
  const toggleBtn = document.getElementById('theme-toggle-btn');
  const savedTheme = localStorage.getItem('pulse_theme') || 'dark';
  
  document.documentElement.setAttribute('data-theme', savedTheme);
  updateThemeIcon(savedTheme);

  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('pulse_theme', newTheme);
      updateThemeIcon(newTheme);
      showToast(`Switched to ${newTheme} mode`, 'info');
    });
  }
}

function updateThemeIcon(theme) {
  const toggleBtn = document.getElementById('theme-toggle-btn');
  if (toggleBtn) {
    toggleBtn.innerHTML = theme === 'dark' ? '☀️' : '🌙';
    toggleBtn.setAttribute('title', `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`);
  }
}

// Initialize Post Composer (Image preview & Async posting)
function initPostComposer() {
  const composerForm = document.getElementById('composer-form');
  const fileInput = document.getElementById('post-image-input');
  const previewWrapper = document.getElementById('composer-preview-wrapper');
  const previewImg = document.getElementById('composer-preview-img');
  const removePreviewBtn = document.getElementById('remove-preview-btn');
  const textarea = document.getElementById('composer-textarea');
  const submitBtn = document.getElementById('composer-submit-btn');

  if (fileInput && previewWrapper && previewImg) {
    fileInput.addEventListener('change', () => {
      const file = fileInput.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          previewImg.src = e.target.result;
          previewWrapper.style.display = 'inline-block';
        };
        reader.readAsDataURL(file);
      }
    });

    if (removePreviewBtn) {
      removePreviewBtn.addEventListener('click', () => {
        fileInput.value = '';
        previewImg.src = '';
        previewWrapper.style.display = 'none';
      });
    }
  }

  if (composerForm) {
    composerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const content = textarea ? textarea.value.trim() : '';
      const hasFile = fileInput && fileInput.files.length > 0;

      if (!content && !hasFile) {
        showToast('Please type some thoughts or select an image.', 'error');
        return;
      }

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span>Publishing...</span>';
      }

      const formData = new FormData(composerForm);

      try {
        const response = await fetch('/api/post/create/', {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrftoken,
          },
          body: formData,
        });

        const data = await response.json();

        if (response.ok && data.status === 'success') {
          showToast(data.message, 'success');
          
          // Clear form
          if (textarea) textarea.value = '';
          if (fileInput) fileInput.value = '';
          if (previewWrapper) previewWrapper.style.display = 'none';

          // Insert new post card directly into feed
          insertNewPostIntoFeed(data.post);
        } else {
          showToast(data.message || 'Error creating post.', 'error');
        }
      } catch (err) {
        console.error(err);
        showToast('Network error while creating post.', 'error');
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = '<span>Post</span> <span style="font-size:16px;">🚀</span>';
        }
      }
    });
  }
}

// Dynamically construct and prepend a new post card
function insertNewPostIntoFeed(post) {
  const postsFeed = document.getElementById('posts-feed-container');
  if (!postsFeed) return;

  const emptyState = document.getElementById('empty-feed-state');
  if (emptyState) emptyState.remove();

  const card = document.createElement('article');
  card.className = 'post-card';
  card.id = `post-${post.id}`;
  card.style.animation = 'slideDown 0.4s cubic-bezier(0.16, 1, 0.3, 1)';

  let imageHtml = '';
  if (post.image_url) {
    imageHtml = `
      <div class="post-media-wrapper" onclick="openLightbox('${post.image_url}')">
        <img src="${post.image_url}" alt="Post media" class="post-media-img" loading="lazy">
      </div>
    `;
  }

  card.innerHTML = `
    <header class="post-header">
      <div class="post-author-block">
        <a href="/profile/${post.author_username}/">
          <img src="${post.author_avatar}" alt="${post.author_name}" class="post-avatar">
        </a>
        <div>
          <a href="/profile/${post.author_username}/" class="post-author-name">
            ${escapeHtml(post.author_name)}
          </a>
          <div class="post-meta-sub">
            <span>@${post.author_username}</span>
            <span class="post-dot">●</span>
            <span>${post.created_at}</span>
          </div>
        </div>
      </div>
      <div class="post-options-dropdown">
        <button class="post-options-btn" onclick="deletePost(${post.id})" title="Delete post">🗑️</button>
      </div>
    </header>

    <div class="post-content">
      ${formatPostContent(post.content)}
    </div>

    ${imageHtml}

    <footer class="post-actions-footer">
      <button class="action-btn like-btn" onclick="toggleLike(${post.id}, this)" id="like-btn-${post.id}">
        <span class="heart-icon">🤍</span>
        <span class="like-count">0</span>
      </button>

      <button class="action-btn comment-btn" onclick="toggleComments(${post.id})">
        <span>💬</span>
        <span class="comment-count" id="comment-count-${post.id}">0</span>
      </button>

      <button class="action-btn bookmark-btn" onclick="toggleBookmark(${post.id}, this)">
        <span>🔖</span>
      </button>

      <button class="action-btn share-btn" onclick="sharePost(${post.id})">
        <span>🔗</span>
      </button>
    </footer>

    <section class="comments-container" id="comments-section-${post.id}">
      <form class="comment-input-row" onsubmit="submitComment(event, ${post.id})">
        <input type="text" class="comment-input-box" placeholder="Write a comment..." required>
        <button type="submit" class="comment-submit-btn">Send</button>
      </form>
      <div class="comments-list" id="comments-list-${post.id}"></div>
    </section>
  `;

  postsFeed.prepend(card);
}

// Toggle Like
async function toggleLike(postId, btn) {
  try {
    const res = await fetch(`/api/post/${postId}/like/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json'
      }
    });

    if (res.status === 401 || res.status === 403 || res.redirected) {
      showToast('Please log in to like posts!', 'info');
      setTimeout(() => {
        window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
      }, 500);
      return;
    }

    const data = await res.json();
    if (data.status === 'success') {
      const heartIcon = btn.querySelector('.heart-icon');
      const countSpan = btn.querySelector('.like-count');

      if (data.liked) {
        btn.classList.add('liked');
        heartIcon.textContent = '❤️';
        showToast('Liked post! ❤️', 'success');
      } else {
        btn.classList.remove('liked');
        heartIcon.textContent = '🤍';
        showToast('Unliked post', 'info');
      }

      if (countSpan) {
        countSpan.textContent = data.likes_count;
      }
    } else if (data.status === 'login_required') {
      showToast('Please log in to like posts!', 'info');
      setTimeout(() => {
        window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
      }, 500);
    }
  } catch (err) {
    console.error('Like toggle failed:', err);
    showToast('Failed to update like.', 'error');
  }
}

// Toggle Bookmark
async function toggleBookmark(postId, btn) {
  try {
    const res = await fetch(`/api/post/${postId}/bookmark/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json'
      }
    });

    if (res.status === 403 || res.redirected) {
      window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
      return;
    }

    const data = await res.json();
    if (data.status === 'success') {
      if (data.bookmarked) {
        btn.classList.add('bookmarked');
        btn.innerHTML = '<span>🏷️</span>';
        showToast('Saved to your bookmarks!', 'success');
      } else {
        btn.classList.remove('bookmarked');
        btn.innerHTML = '<span>🔖</span>';
        showToast('Removed from bookmarks.', 'info');
      }
    }
  } catch (err) {
    console.error('Bookmark failed:', err);
  }
}

// Toggle Comment Section
function toggleComments(postId) {
  const section = document.getElementById(`comments-section-${postId}`);
  if (section) {
    section.classList.toggle('show');
    if (section.classList.contains('show')) {
      const input = section.querySelector('.comment-input-box');
      if (input) input.focus();
    }
  }
}

// Submit a new Comment
async function submitComment(event, postId) {
  event.preventDefault();
  const form = event.target;
  const input = form.querySelector('.comment-input-box');
  const content = input ? input.value.trim() : '';

  if (!content) return;

  try {
    const res = await fetch(`/api/post/${postId}/comment/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ content: content })
    });

    if (res.status === 403 || res.redirected) {
      window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
      return;
    }

    const data = await res.json();
    if (data.status === 'success') {
      input.value = '';
      
      // Update comment count on post
      const countSpan = document.getElementById(`comment-count-${postId}`);
      if (countSpan) countSpan.textContent = data.comments_count;

      // Add comment item to list
      const list = document.getElementById(`comments-list-${postId}`);
      if (list) {
        const comment = data.comment;
        const item = document.createElement('div');
        item.className = 'comment-item';
        item.id = `comment-${comment.id}`;
        item.innerHTML = `
          <a href="/profile/${comment.author_username}/">
            <img src="${comment.author_avatar}" alt="${comment.author_name}" class="comment-avatar">
          </a>
          <div class="comment-body">
            <div class="comment-meta">
              <a href="/profile/${comment.author_username}/" class="comment-author">${escapeHtml(comment.author_name)}</a>
              <span class="comment-time">${comment.created_at}</span>
              <button class="comment-delete-btn" onclick="deleteComment(${comment.id}, ${postId})" title="Delete">✕</button>
            </div>
            <p class="comment-text">${escapeHtml(comment.content)}</p>
          </div>
        `;
        list.appendChild(item);
      }
      showToast('Comment posted!', 'success');
    } else {
      showToast(data.message || 'Failed to post comment', 'error');
    }
  } catch (err) {
    console.error(err);
    showToast('Network error while commenting.', 'error');
  }
}

// Delete Comment
async function deleteComment(commentId, postId) {
  if (!confirm('Are you sure you want to delete this comment?')) return;

  try {
    const res = await fetch(`/api/comment/${commentId}/delete/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrftoken }
    });
    const data = await res.json();
    if (data.status === 'success') {
      const item = document.getElementById(`comment-${commentId}`);
      if (item) item.remove();
      
      const countSpan = document.getElementById(`comment-count-${postId}`);
      if (countSpan) countSpan.textContent = data.comments_count;
      
      showToast('Comment deleted', 'info');
    }
  } catch (err) {
    console.error(err);
    showToast('Failed to delete comment', 'error');
  }
}

// Delete Post
async function deletePost(postId) {
  if (!confirm('Are you sure you want to permanently delete this post?')) return;

  try {
    const res = await fetch(`/api/post/${postId}/delete/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrftoken }
    });
    const data = await res.json();
    if (data.status === 'success') {
      const card = document.getElementById(`post-${postId}`);
      if (card) {
        card.style.opacity = '0';
        card.style.transform = 'scale(0.95)';
        setTimeout(() => card.remove(), 250);
      }
      showToast('Post removed', 'info');
    } else {
      showToast(data.message || 'Permission denied', 'error');
    }
  } catch (err) {
    console.error(err);
    showToast('Error deleting post', 'error');
  }
}

// Toggle Follow
async function toggleFollow(username, btn) {
  try {
    const res = await fetch(`/api/user/${username}/follow/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrftoken }
    });

    if (res.status === 403 || res.redirected) {
      window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
      return;
    }

    const data = await res.json();
    if (data.status === 'success') {
      if (data.is_following) {
        btn.classList.add('following');
        btn.textContent = 'Following';
        showToast(`Now following @${username}`, 'success');
      } else {
        btn.classList.remove('following');
        btn.textContent = 'Follow';
        showToast(`Unfollowed @${username}`, 'info');
      }

      // Update follower count metric if present on profile page
      const countEl = document.getElementById('profile-followers-count');
      if (countEl) {
        countEl.textContent = data.followers_count;
      }
    } else {
      showToast(data.message || 'Failed to update follow status', 'error');
    }
  } catch (err) {
    console.error(err);
    showToast('Failed to follow user', 'error');
  }
}

// Open Followers / Following Modal
async function openUsersModal(type, username) {
  const modal = document.getElementById('users-list-modal');
  const title = document.getElementById('users-modal-title');
  const container = document.getElementById('users-modal-list');

  if (!modal || !title || !container) return;

  title.textContent = type === 'followers' ? 'Followers' : 'Following';
  container.innerHTML = '<div style="text-align:center; padding:30px; color:var(--text-muted)">Loading...</div>';
  modal.classList.add('active');

  try {
    const res = await fetch(`/api/user/${username}/${type}/`);
    const data = await res.json();

    if (data.status === 'success') {
      if (data.users.length === 0) {
        container.innerHTML = `<div style="text-align:center; padding:30px; color:var(--text-muted)">No ${type} yet.</div>`;
        return;
      }

      container.innerHTML = data.users.map(u => `
        <div class="suggested-user-row" style="padding:10px 0; border-bottom:1px solid var(--border-color);">
          <div class="suggested-user-info">
            <a href="/profile/${u.username}/">
              <img src="${u.avatar}" class="suggested-user-avatar" alt="${escapeHtml(u.name)}">
            </a>
            <div class="suggested-user-details">
              <a href="/profile/${u.username}/" class="suggested-user-name">${escapeHtml(u.name)}</a>
              <div class="suggested-user-handle">@${u.username}</div>
              ${u.bio ? `<div style="font-size:12px; color:var(--text-secondary); margin-top:2px;">${escapeHtml(u.bio)}</div>` : ''}
            </div>
          </div>
          ${!u.is_self ? `
            <button class="btn-follow ${u.is_following ? 'following' : ''}" onclick="toggleFollow('${u.username}', this)">
              ${u.is_following ? 'Following' : 'Follow'}
            </button>
          ` : ''}
        </div>
      `).join('');
    }
  } catch (err) {
    console.error(err);
    container.innerHTML = '<div style="text-align:center; padding:30px; color:var(--accent-like)">Failed to load users.</div>';
  }
}

// Close any active modal
function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.remove('active');
}

// Edit Profile Modal Helpers
function openEditProfileModal() {
  const modal = document.getElementById('edit-profile-modal');
  if (modal) modal.classList.add('active');
}

// Share post helper
function sharePost(postId) {
  const url = `${window.location.origin}/post/${postId}/`;
  navigator.clipboard.writeText(url).then(() => {
    showToast('Post link copied to clipboard!', 'success');
  }).catch(() => {
    prompt('Copy link:', url);
  });
}

// Image Lightbox
function openLightbox(imgUrl) {
  let modal = document.getElementById('lightbox-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'lightbox-modal';
    modal.className = 'modal-backdrop';
    modal.innerHTML = `
      <div style="position:relative; max-width:90vw; max-height:90vh;">
        <button onclick="closeModal('lightbox-modal')" style="position:absolute; top:-40px; right:0; color:#fff; font-size:28px;">✕</button>
        <img id="lightbox-img" src="" style="max-width:90vw; max-height:85vh; border-radius:12px; box-shadow:var(--shadow-lg); object-fit:contain;">
      </div>
    `;
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeModal('lightbox-modal');
    });
    document.body.appendChild(modal);
  }

  document.getElementById('lightbox-img').src = imgUrl;
  modal.classList.add('active');
}

// Live Search with Debounce
function initLiveSearch() {
  const input = document.getElementById('global-search-input');
  const dropdown = document.getElementById('search-dropdown');
  if (!input || !dropdown) return;

  let debounceTimer;

  input.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    const q = input.value.trim();

    if (!q) {
      dropdown.classList.remove('show');
      return;
    }

    debounceTimer = setTimeout(async () => {
      try {
        const res = await fetch(`/api/search/?q=${encodeURIComponent(q)}`);
        const data = await res.json();

        let html = '';
        if (data.users.length > 0) {
          html += '<div style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; margin-bottom:6px; letter-spacing:0.5px;">Users</div>';
          html += data.users.map(u => `
            <a href="/profile/${u.username}/" class="search-result-item">
              <img src="${u.avatar}" style="width:28px; height:28px; border-radius:50%; object-fit:cover;">
              <div>
                <div style="font-weight:700; font-size:13px; color:var(--text-primary);">${escapeHtml(u.name)}</div>
                <div style="font-size:11px; color:var(--text-muted);">@${u.username}</div>
              </div>
            </a>
          `).join('');
        }

        if (data.posts.length > 0) {
          html += '<div style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; margin:10px 0 6px; letter-spacing:0.5px;">Posts</div>';
          html += data.posts.map(p => `
            <a href="/post/${p.id}/" class="search-result-item">
              <span>💬</span>
              <div style="font-size:12px; color:var(--text-secondary); line-height:1.4;">${escapeHtml(p.content)}</div>
            </a>
          `).join('');
        }

        if (!data.users.length && !data.posts.length) {
          html = '<div style="text-align:center; padding:12px; font-size:13px; color:var(--text-muted);">No results found</div>';
        }

        dropdown.innerHTML = html;
        dropdown.classList.add('show');
      } catch (e) {
        console.error(e);
      }
    }, 250);
  });

  document.addEventListener('click', (e) => {
    if (!input.contains(e.target) && !dropdown.contains(e.target)) {
      dropdown.classList.remove('show');
    }
  });
}

// Utility: format post content with hashtags
function formatPostContent(text) {
  if (!text) return '';
  const escaped = escapeHtml(text);
  // Highlight hashtags
  return escaped.replace(/#(\w+)/g, '<a href="/explore/?q=%23$1" class="hashtag">#$1</a>');
}

function escapeHtml(string) {
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(string));
  return div.innerHTML;
}

// Global initialization on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
  initThemeToggle();
  initPostComposer();
  initLiveSearch();

  // Close modals on clicking backdrop
  document.querySelectorAll('.modal-backdrop').forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.classList.remove('active');
    });
  });
});
