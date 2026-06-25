// forum page
document.addEventListener('DOMContentLoaded', () => {
  loadPosts();

  document.getElementById('openNewPost').addEventListener('click', () => {
    document.getElementById('newPostModal').classList.add('open');
  });

  document.getElementById('closeNewPost').addEventListener('click', () => {
    document.getElementById('newPostModal').classList.remove('open');
  });

  document.getElementById('newPostForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const form  = e.target;
    const error = document.getElementById('postError');
    const body  = {
      title:    form.title.value,
      body:     form.body.value,
      crop_tag: form.crop_tag.value,
    };

    const res = await apiFetch('/api/forum/posts/', {
      method: 'POST',
      body:   JSON.stringify(body),
    });

    if (res && res.ok) {
      document.getElementById('newPostModal').classList.remove('open');
      form.reset();
      loadPosts();
    } else {
      const data    = await res.json();
      error.textContent = Object.values(data).flat().join(' ');
    }
  });
});

async function loadPosts() {
  const list = document.getElementById('postsList');
  list.innerHTML = '<p class="loading-text">loading posts...</p>';
  const res  = await apiFetch('/api/forum/posts/');
  if (!res || !res.ok) return;
  const data  = await res.json();
  const posts = data.results || data;
  list.innerHTML = '';

  if (!posts.length) {
    list.innerHTML = '<p class="loading-text">no posts yet. be the first to ask a question.</p>';
    return;
  }

  posts.forEach(post => {
    list.innerHTML += `
      <div class="post-item">
        <h4>${post.title}</h4>
        <p>${post.body.substring(0, 120)}${post.body.length > 120 ? '...' : ''}</p>
        <div class="post-meta">
          <span>${post.author_name}</span>
          <span>${post.reply_count} replies</span>
          <span>${new Date(post.created_at).toLocaleDateString()}</span>
          ${post.crop_tag ? `<span class="crop-tag">${post.crop_tag}</span>` : ''}
        </div>
      </div>`;
  });
}
