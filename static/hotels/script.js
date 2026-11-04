/* ---------------------------
   Login Page
----------------------------*/
const loginForm = document.getElementById('login-form');
if(loginForm){
  const idf = document.getElementById('identifier');
  const pwd = document.getElementById('password');
  const idErr = document.getElementById('identifier-error');
  const pwErr = document.getElementById('password-error');
  const toggle = document.getElementById('togglePass');
  const demo = document.getElementById('demoLogin');

  toggle?.addEventListener('click', ()=>{
    const type = pwd.type === 'password' ? 'text' : 'password';
    pwd.type = type;
    toggle.textContent = type === 'password' ? '👁️' : '🙈';
    toggle.title = type === 'password' ? 'Show password' : 'Hide password';
  });

  demo?.addEventListener('click', ()=>{
    idf.value = 'demo@luxera.test';
    pwd.value = 'demopassword';
    idErr.hidden = true; pwErr.hidden = true;
  });

  function validateIdentifier(v){
    if(!v) return 'Please enter email or phone.';
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const phonePattern = /^[+\d][\d\s-()]{6,}$/;
    if(emailPattern.test(v) || phonePattern.test(v)) return '';
    return 'Enter a valid email or phone number.';
  }

  function validatePassword(v){
    if(!v) return 'Please enter your password.';
    if(v.length<6) return 'Password must be at least 6 characters.';
    return '';
  }

  loginForm.addEventListener('submit',(e)=>{
    e.preventDefault();
    let hasError=false;
    const idMsg = validateIdentifier(idf.value.trim());
    const pwMsg = validatePassword(pwd.value);
    if(idMsg){idErr.textContent=idMsg;idErr.hidden=false;hasError=true;} else{idErr.hidden=true;}
    if(pwMsg){pwErr.textContent=pwMsg;pwErr.hidden=false;hasError=true;} else{pwErr.hidden=true;}
    if(!hasError){ alert('Form valid — ready to send to server.'); loginForm.reset(); }
  });

  idf.addEventListener('blur',()=>{ const msg = validateIdentifier(idf.value.trim()); if(msg){idErr.textContent=msg;idErr.hidden=false;} else{idErr.hidden=true;} });
  pwd.addEventListener('blur',()=>{ const msg = validatePassword(pwd.value); if(msg){pwErr.textContent=msg;pwErr.hidden=false;} else{pwErr.hidden=true;} });
}

/* ---------------------------
   Home Page Filters
----------------------------*/
const applyBtn = document.getElementById('apply-filters');
if(applyBtn){
  applyBtn.addEventListener('click', ()=>{
    const minBudget = parseInt(document.getElementById('min-budget').value);
    const maxBudget = parseInt(document.getElementById('max-budget').value);
    const prepayment = document.getElementById('prepayment').checked;
    const freeCancel = document.getElementById('free-cancel').checked;
    const breakfast = document.getElementById('breakfast').checked;
    const selectedTypes = Array.from(document.querySelectorAll('.property-type:checked')).map(cb=>cb.value);

    const hotels = document.querySelectorAll('.hotel');
    let visibleCount = 0;
    hotels.forEach(hotel=>{
      const price = parseInt(hotel.dataset.price);
      const matchesBudget = price >= minBudget && price <= maxBudget;
      const matchesType = selectedTypes.length===0 || selectedTypes.includes(hotel.dataset.type);
      const matchesPrepay = !prepayment || hotel.dataset.prepayment==='true';
      const matchesCancel = !freeCancel || hotel.dataset.cancel==='true';
      const matchesBreakfast = !breakfast || hotel.dataset.breakfast==='true';
      if(matchesBudget && matchesType && matchesPrepay && matchesCancel && matchesBreakfast){ hotel.style.display='block'; visibleCount++; }
      else{ hotel.style.display='none'; }
    });
    document.getElementById('no-results').style.display = visibleCount===0 ? 'block':'none';
  });
}
