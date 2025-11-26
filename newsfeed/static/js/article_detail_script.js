// newsfeed/static/js/article_detail_script.js

document.addEventListener('DOMContentLoaded', function() {

    // Function to get CSRF token (Mandatory for Django POST requests)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                let cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    // Find any action button to safely retrieve the article ID
    const actionButton = document.querySelector('.article-actions button[data-article-id]');
    if (!actionButton) return;

    const articleId = actionButton.dataset.articleId;

    // ===========================================================
    // 1. LIKE / SAVE TOGGLE FUNCTIONALITY (Uses API endpoints)
    // ===========================================================
    const actionButtons = document.querySelectorAll('.action-btn[data-article-id]');

    actionButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const action = this.dataset.action; // 'like' or 'save'

            if (!csrftoken) {
                // User is not authenticated
                alert("Please log in to perform this action.");
                window.location.href = '/news/login/';
                return;
            }

            let endpoint = '';
            if (action === 'like') {
                // Corrected endpoint with /news/ prefix
                endpoint = `/news/like/${articleId}/`;
            } else if (action === 'save') {
                // Corrected endpoint with /news/ prefix
                endpoint = `/news/save/${articleId}/`;
            } else {
                return;
            }

            try {
                // API Call
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({})
                });

                const data = await response.json();

                if (response.ok) {
                    const toggleClass = action === 'like' ? 'liked' : 'saved';

                    // Update button styling based on action type
                    if (data.action === 'liked' || data.action === 'saved') {
                        this.classList.add(toggleClass);
                    } else if (data.action === 'unliked' || data.action === 'unsaved') {
                        this.classList.remove(toggleClass);
                    }

                    // Update Like Count (only for like button)
                    if (action === 'like') {
                        const likeCountElement = document.getElementById(`like-count-${articleId}`);
                        if (likeCountElement) {
                            let currentCount = parseInt(likeCountElement.textContent);
                            if (data.action === 'liked') {
                                likeCountElement.textContent = currentCount + 1;
                            } else if (data.action === 'unliked') {
                                likeCountElement.textContent = currentCount - 1;
                            }
                        }
                    }

                } else {
                    alert(`Action failed: ${data.message || 'Server Error'}`);
                }

            } catch (error) {
                console.error('Error during action:', error);
                alert("An error occurred. Please try again.");
            }
        });
    });


    // ===========================================================
    // 2. COMMENT POSTING FUNCTIONALITY (Uses API endpoint)
    // ===========================================================

    const postCommentBtn = document.getElementById('post-comment-btn');
    const commentTextarea = document.getElementById('comment-text');

    if (postCommentBtn) {
        postCommentBtn.addEventListener('click', async function() {
            const content = commentTextarea.value.trim();

            if (content.length === 0) {
                alert("Comment cannot be empty.");
                return;
            }

            try {
                // API Call to post comment
                const response = await fetch(`/news/comment/${articleId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ content: content })
                });

                const data = await response.json();

                if (response.ok) {
                    alert(data.message);
                    commentTextarea.value = ''; // Clear the textarea
                    // Future improvement: Dynamically load and display the new comment here
                } else {
                    alert(`Failed to post comment: ${data.message || 'Server Error'}`);
                }

            } catch (error) {
                console.error('Error posting comment:', error);
                alert("An error occurred while posting comment.");
            }
        });
    }

    // Future step: Implement loadComments(articleId) to fetch and display existing comments
});