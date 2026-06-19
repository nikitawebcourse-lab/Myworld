// Main JS file for MyWorld interactions

document.addEventListener('DOMContentLoaded', function() {
    // 1. Theme Toggle Logic
    const themeToggleBtn = document.getElementById('themeToggle');
    const body = document.body;
    
    // Check local storage for saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        body.classList.add('light-theme');
        updateThemeToggleIcon('light');
    } else {
        body.classList.remove('light-theme');
        updateThemeToggleIcon('dark');
    }
    
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', function() {
            body.classList.toggle('light-theme');
            const isLight = body.classList.contains('light-theme');
            localStorage.setItem('theme', isLight ? 'light' : 'dark');
            updateThemeToggleIcon(isLight ? 'light' : 'dark');
        });
    }
    
    function updateThemeToggleIcon(theme) {
        if (!themeToggleBtn) return;
        if (theme === 'light') {
            themeToggleBtn.innerHTML = '<i class="bi bi-moon-fill"></i>';
        } else {
            themeToggleBtn.innerHTML = '<i class="bi bi-sun-fill"></i>';
        }
    }

    // Get CSRF token helper
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

    // 2. AJAX Likes
    const likeButtons = document.querySelectorAll('.like-btn');
    likeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const itemId = this.getAttribute('data-item-id');
            const likeUrl = `/like/${itemId}/`;
            
            fetch(likeUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const countSpan = this.querySelector('.like-count');
                    const heartIcon = this.querySelector('i');
                    
                    countSpan.textContent = data.like_count;
                    if (data.liked) {
                        this.classList.add('liked');
                        heartIcon.classList.remove('bi-heart');
                        heartIcon.classList.add('bi-heart-fill');
                    } else {
                        this.classList.remove('liked');
                        heartIcon.classList.remove('bi-heart-fill');
                        heartIcon.classList.add('bi-heart');
                    }
                }
            })
            .catch(err => console.error('Error liking item:', err));
        });
    });

    // 3. AJAX Comments
    const commentForms = document.querySelectorAll('.comment-form');
    commentForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const itemId = this.getAttribute('data-item-id');
            const commentUrl = `/comment/${itemId}/`;
            const input = this.querySelector('.comment-input');
            const content = input.value.trim();
            
            if (!content) return;
            
            const formData = new FormData();
            formData.append('content', content);
            
            fetch(commentUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    input.value = ''; // clear input
                    
                    // Prepend new comment to comment list
                    const listContainer = document.querySelector(`#commentsList-${itemId}`);
                    const noCommentsPlaceholder = document.querySelector(`#noComments-${itemId}`);
                    
                    if (noCommentsPlaceholder) {
                        noCommentsPlaceholder.remove();
                    }
                    
                    const commentHTML = `
                        <div class="d-flex mb-3 align-items-start">
                            <img src="${data.comment.avatar_url}" alt="avatar" class="rounded-circle me-2" style="width: 32px; height: 32px; object-fit: cover; border: 1px solid var(--border-color);">
                            <div class="p-2 glass-card flex-grow-1" style="background: rgba(255,255,255,0.03); border-radius: 12px; font-size: 0.85rem;">
                                <div class="d-flex justify-content-between">
                                    <strong>${data.comment.username}</strong>
                                    <small class="text-muted" style="font-size: 0.75rem;">${data.comment.created_at}</small>
                                </div>
                                <div class="mt-1">${data.comment.content}</div>
                            </div>
                        </div>
                    `;
                    listContainer.insertAdjacentHTML('beforeend', commentHTML);
                    
                    // Scroll to bottom of comments list
                    listContainer.scrollTop = listContainer.scrollHeight;
                    
                    // Update main card / modal counts
                    const countBadge = document.querySelector(`#commentCountBadge-${itemId}`);
                    if (countBadge) countBadge.textContent = data.comment_count;
                    
                    const modalCountBadge = document.querySelector(`#modalCommentCount-${itemId}`);
                    if (modalCountBadge) modalCountBadge.textContent = data.comment_count;
                }
            })
            .catch(err => console.error('Error posting comment:', err));
        });
    });

    // 4. AJAX Follow/Unfollow
    const followButtons = document.querySelectorAll('.follow-btn-toggle');
    followButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const username = this.getAttribute('data-username');
            const followUrl = `/follow/${username}/`;
            
            fetch(followUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (data.following) {
                        this.classList.add('following');
                        this.textContent = 'Following';
                        this.classList.remove('btn-outline-primary');
                        this.classList.add('btn-primary-custom');
                    } else {
                        this.classList.remove('following');
                        this.textContent = 'Follow';
                        this.classList.add('btn-outline-primary');
                        this.classList.remove('btn-primary-custom');
                    }
                    
                    // Update stats if on profile page
                    const followersCount = document.getElementById('followersCount');
                    if (followersCount) {
                        followersCount.textContent = data.followers_count;
                    }
                }
            })
            .catch(err => console.error('Error following user:', err));
        });
    });

    // 5. Auto Detect Platform Badge in "Add Item" Modal
    const urlInput = document.getElementById('addItemUrl');
    const platformPreview = document.getElementById('platformPreview');
    if (urlInput && platformPreview) {
        urlInput.addEventListener('input', function() {
            const url = this.value.toLowerCase();
            let platform = 'Other';
            let badgeClass = 'platform-other';
            
            if (url.includes('amazon.')) {
                platform = 'Amazon';
                badgeClass = 'platform-amazon';
            } else if (url.includes('flipkart.')) {
                platform = 'Flipkart';
                badgeClass = 'platform-flipkart';
            } else if (url.includes('instagram.com')) {
                platform = 'Instagram';
                badgeClass = 'platform-instagram';
            } else if (url.includes('youtube.com') || url.includes('youtu.be')) {
                platform = 'YouTube';
                badgeClass = 'platform-youtube';
            } else if (url.includes('facebook.com')) {
                platform = 'Facebook';
                badgeClass = 'platform-facebook';
            }
            
            if (url.trim() === '') {
                platformPreview.style.display = 'none';
            } else {
                platformPreview.className = `platform-badge ${badgeClass} position-relative d-inline-block mt-2 mb-2`;
                platformPreview.textContent = `Auto-Detected: ${platform}`;
                platformPreview.style.display = 'inline-block';
            }
        });
    }
});
