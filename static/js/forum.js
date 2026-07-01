document.addEventListener('DOMContentLoaded',()=>{
  loadPosts(); loadStats();
  document.getElementById('openNewPost').addEventListener('click',()=>document.getElementById('newPostModal').classList.add('open'));
  document.getElementById('closeNewPost').addEventListener('click',()=>document.getElementById('newPostModal').classList.remove('open'));
  document.getElementById('newPostForm').addEventListener('submit', async (e)=>{
    e.preventDefault(); const form=e.target; const error=document.getElementById('postError'); error.textContent='';
    const res=await apiFetch('/api/forum/posts/',{method:'POST',body:JSON.stringify({title:form.title.value,body:form.body.value,crop_tag:form.crop_tag.value})});
    if(res&&res.ok){document.getElementById('newPostModal').classList.remove('open');form.reset();loadPosts();loadStats();}
    else if(res){const data=await res.json();error.textContent=Object.values(data).flat().join(' ');}
  });
});

async function loadPosts(){
  const list=document.getElementById('postsList'); list.innerHTML='<p class="loading-text">loading...</p>';
  const res=await apiFetch('/api/forum/posts/'); if(!res||!res.ok){list.innerHTML='<p class="loading-text">could not load posts.</p>';return;}
  const data=await res.json(); const posts=data.results||data; list.innerHTML='';
  if(!posts.length){list.innerHTML='<p class="loading-text">no posts yet. be the first to ask a question.</p>';return;}
  posts.forEach(post=>{
    const card=document.createElement('div'); card.className='post-item'; card.id=`post-card-${post.id}`;
    card.innerHTML=`
      <div style="display:flex;justify-content:space-between;align-items:start">
        <div style="flex:1;cursor:pointer" onclick="toggleReplies(${post.id})">
          <h4>${post.title}</h4>
          <p>${post.body.substring(0,140)}${post.body.length>140?'...':''}</p>
          <div class="post-meta">
            <span>${post.author_name||'farmer'}</span>
            <span>${post.reply_count||0} replies</span>
            ${post.crop_tag?`<span class="crop-tag">${post.crop_tag}</span>`:''}
          </div>
        </div>
        <button onclick="upvotePost(${post.id})" style="background:none;border:1px solid #c8ddb8;border-radius:8px;padding:6px 12px;cursor:pointer;color:#4a7c3f;font-size:12px;white-space:nowrap;margin-left:12px" id="upvote-${post.id}">
          ▲ <span id="upvote-count-${post.id}">${post.upvotes||0}</span>
        </button>
      </div>
      <div class="post-replies" id="replies-${post.id}" style="display:none;margin-top:12px;border-top:1px solid #eee;padding-top:10px"></div>`;
    list.appendChild(card);
  });
}

async function upvotePost(postId){
  const res=await apiFetch(`/api/forum/posts/${postId}/upvote/`,{method:'POST'});
  if(res&&res.ok){
    const data=await res.json();
    const btn=document.getElementById(`upvote-${postId}`);
    const count=document.getElementById(`upvote-count-${postId}`);
    if(count) count.textContent=data.upvotes;
    if(btn){btn.style.background='#f0f8e8';btn.style.borderColor='#7ab648';}
    loadStats();
  }
}

async function toggleReplies(postId){
  const box=document.getElementById(`replies-${postId}`);
  if(box.style.display==='block'){box.style.display='none';return;}
  box.style.display='block'; box.innerHTML='<p class="loading-text">loading...</p>';
  const res=await apiFetch(`/api/forum/replies/?post=${postId}`);
  let html=`<div style="display:flex;gap:8px;margin-bottom:10px">
    <button onclick="getAiAnswer(${postId})" class="btn-outline" style="font-size:11px;padding:5px 12px">ask ai co-pilot</button>
  </div>`;
  if(res&&res.ok){
    const data=await res.json(); const replies=data.results||data;
    if(replies.length){
      replies.forEach(r=>{html+=`<div style="padding:8px 0;border-bottom:1px solid #f5f5f5">
        <strong style="font-size:12px;color:${r.is_expert?'#4a7c3f':'#333'}">${r.author_name||'user'}${r.is_expert?' ✓ expert':''}</strong>
        <p style="font-size:13px;color:#555;margin-top:4px;white-space:pre-wrap">${r.body.replace('[ai co-pilot]\n\n','')}</p>
      </div>`;});
    } else html+='<p class="loading-text">no replies yet.</p>';
  }
  html+=`<div style="display:flex;gap:6px;margin-top:10px">
    <input type="text" id="reply-input-${postId}" placeholder="write a reply..." style="flex:1;padding:8px 10px;border:1px solid #ddd;border-radius:8px;font-size:13px">
    <button onclick="sendReply(${postId})" class="btn-primary" style="font-size:12px;padding:8px 14px">send</button>
  </div>`;
  box.innerHTML=html;
}

async function getAiAnswer(postId){
  const res=await apiFetch(`/api/forum/posts/${postId}/ai_answer/`,{method:'POST'});
  if(res&&res.ok){
    document.getElementById(`replies-${postId}`).style.display='none';
    toggleReplies(postId); loadPosts();
  }
}

async function sendReply(postId){
  const input=document.getElementById(`reply-input-${postId}`); const body=input.value.trim(); if(!body)return;
  const res=await apiFetch('/api/forum/replies/',{method:'POST',body:JSON.stringify({post:postId,body})});
  if(res&&res.ok){input.value='';document.getElementById(`replies-${postId}`).style.display='none';toggleReplies(postId);loadPosts();}
}

async function loadStats(){
  const res=await apiFetch('/api/forum/posts/'); if(!res||!res.ok)return;
  const data=await res.json(); const posts=data.results||data;
  document.getElementById('communityStats').innerHTML=`
    <strong>${posts.length}</strong> posts<br>
    <strong>${posts.reduce((s,p)=>s+(p.reply_count||0),0)}</strong> replies<br>
    <strong>${posts.reduce((s,p)=>s+(p.upvotes||0),0)}</strong> upvotes`;
}
