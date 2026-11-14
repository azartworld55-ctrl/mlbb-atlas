const DATA = {heroes:[],items:[],skills:[]};
const $ = (s,root=document)=>root.querySelector(s);
const $$ = (s,root=document)=>[...root.querySelectorAll(s)];
const state = {view:"heroes",role:"all",lane:"all",query:"",favoritesOnly:false,itemCategory:"all",itemQuery:""};
const roleNames={Tank:"Танк",Fighter:"Боец",Assassin:"Убийца",Mage:"Маг",Marksman:"Стрелок",Support:"Поддержка"};
const laneNames={"exp lane":"EXP","gold lane":"Золото","mid lane":"Мид","jungle":"Лес","roam":"Роум"};
const categoryNames={Attack:"Атака",Magic:"Магия",Defense:"Защита",Movement:"Передвижение",Jungle:"Лес",Roaming:"Роум"};
const safe=(v)=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const favKey="mlbb-atlas-favorites-v1";
function getFavorites(){try{return new Set(JSON.parse(localStorage.getItem(favKey)||"[]"))}catch{return new Set()}}
let favorites=getFavorites();
function saveFavorites(){localStorage.setItem(favKey,JSON.stringify([...favorites]))}
function translateRole(r){return roleNames[r]||r||"—"}
function translateLane(l){return laneNames[String(l||"").toLowerCase()]||l||"—"}
function imageUrl(hero){return hero.assets?.portrait_url||""}
function sourceBadge(status){return status==="verified"?"Проверено":status==="experimental"?"Экспериментально":"Сообщено источником"}
async function loadData(){
  const files=["heroes","items","skills"];
  const [heroes,items,skills]=await Promise.all(files.map(f=>fetch("./data/"+f+".json").then(r=>{if(!r.ok)throw Error("Не удалось загрузить "+f);return r.json()})));
  DATA.heroes=heroes;DATA.items=items;DATA.skills=skills;
  $("#metric-heroes").textContent=heroes.length;$("#metric-items").textContent=items.length;$("#metric-skills").textContent=skills.length;
  renderHeroes();renderItems();renderSkills();
}
function renderHeroes(){
  const query=state.query.trim().toLocaleLowerCase("ru");
  const rows=DATA.heroes.filter(h=>(state.role==="all"||h.roles?.includes(state.role))&&(state.lane==="all"||h.lanes?.some(l=>l.toLowerCase()===state.lane))&&(!state.favoritesOnly||favorites.has(h.slug||h.id))&&(!query||[h.name,h.slug,...(h.roles||[]),...(h.lanes||[])].join(" ").toLocaleLowerCase("ru").includes(query))).sort((a,b)=>a.name.localeCompare(b.name,"ru"));
  $("#result-count").textContent=rows.length+" / "+DATA.heroes.length+" героев";
  $("#hero-grid").innerHTML=rows.map(h=>{const id=h.slug||h.id;const roles=(h.roles||[]).map(translateRole).join(" · ");const lanes=(h.lanes||[]).map(translateLane).join(" / ");return `<article class="hero-card" data-hero="${safe(id)}" tabindex="0" role="button" aria-label="Открыть героя ${safe(h.name)}"><div class="portrait">${imageUrl(h)?`<img loading="lazy" src="${safe(imageUrl(h))}" alt="" onerror="this.style.display='none'">`:""}<span class="role-chip">${safe(translateRole(h.roles?.[0]))}</span><button class="favorite ${favorites.has(id)?"saved":""}" data-fav="${safe(id)}" aria-label="В избранное">${favorites.has(id)?"★":"☆"}</button></div><div class="hero-info"><div class="hero-name">${safe(h.name)}</div><div class="hero-meta"><span>${safe(roles)}</span><span>${safe(lanes)}</span></div></div></article>`}).join("");
  $("#empty-state").classList.toggle("hidden",rows.length!==0);
  $("#pagination-note").textContent=rows.length?"Показаны все найденные герои":"";
}
function renderItems(){
 const q=state.itemQuery.toLocaleLowerCase("ru");
 const rows=DATA.items.filter(i=>(state.itemCategory==="all"||i.category===state.itemCategory)&&(!q||(i.name+" "+i.category+" "+i.summary+" "+(i.unique_passive||[]).map(p=>p.description).join(" ")).toLocaleLowerCase("ru").includes(q)));
 $("#item-grid").innerHTML=rows.map(i=>{const desc=(i.unique_passive||[]).map(p=>p.description).filter(x=>x&&x!=="null").join(" · ")||i.summary||"Описание отсутствует";return `<article class="item-card"><div class="item-category">${safe(categoryNames[i.category]||i.category||"ПРЕДМЕТ")}</div><h3>${safe(i.name)}</h3><div class="item-cost">${i.cost&&i.cost!=="null"?safe(i.cost)+" золота":"Стоимость не указана"}</div><p>${safe(desc)}</p><small class="muted">${safe(i.provenance?.confidence||"Статус не указан")} · источник: ${safe(i.provenance?.source_repository||"не указан")}</small></article>`}).join("");
}
function renderSkills(){
 const q=$("#skill-search").value.toLocaleLowerCase("ru"),patch=$("#patch-filter").value,status=$("#status-filter").value;
 const rows=DATA.skills.filter(r=>(patch==="all"||r.patch?.version===patch)&&(status==="all"||r.verification?.status===status)&&(!q||[r.hero_id,r.skill_name,r.patch?.version].join(" ").toLocaleLowerCase("ru").includes(q)));
 $("#skill-list").innerHTML=rows.map(r=>{const params=(r.parameters||[]).map(p=>{const vals=(p.values_by_skill_level||[]).join(" → ")||"значение не опубликовано";const meaning=p.value_semantics==="endpoints"?" · границы":p.value_semantics==="per_level"?" · по уровням":"";return `<span class="parameter">${safe(p.key)}: ${safe(vals)} ${safe(p.unit||"")}${meaning}</span>`}).join("");const src=(r.sources||[]).find(s=>s.url);return `<article class="skill-card"><div class="skill-card-head"><div><h3>${safe(r.skill_name)} <span style="color:#9aa4b1;font-size:12px">· ${safe(r.hero_id)}</span></h3><div class="skill-meta">Патч ${safe(r.patch?.version)} · ${safe(r.patch?.channel)} · ${safe(r.patch?.effective_from||"дата не указана")}</div></div><span class="status-tag ${safe(r.verification?.status)}">${safe(sourceBadge(r.verification?.status))}</span></div><div class="skill-parameters">${params||'<span class="parameter">Числовые параметры не опубликованы</span>'}</div><div class="skill-meta">${safe(r.verification?.notes||"")}</div>${src?`<a class="source-link" href="${safe(src.url)}" target="_blank" rel="noopener">Открыть источник ↗</a>`:""}</article>`}).join("")||'<div class="empty-state">Записей по выбранным условиям нет.</div>';
}
function openHero(id){
 const h=DATA.heroes.find(x=>(x.slug||x.id)===id);if(!h)return;
 const records=DATA.skills.filter(r=>r.hero_id===id);
 const skills=(h.skills||[]).map(s=>`<div class="modal-skill"><b>${safe(s.name)} <small style="color:#8e9aa8;font:10px Manrope">· ${safe(s.type)}</small></b><p>${safe(s.description||"Описание пока отсутствует.")}</p></div>`).join("");
 $("#modal-content").innerHTML=`<div class="modal-hero">${imageUrl(h)?`<img class="modal-portrait" src="${safe(imageUrl(h))}" alt="">`:'<div class="modal-portrait"></div>'}<div><div class="overline">КАРТОЧКА ГЕРОЯ</div><h2 id="modal-name">${safe(h.name)}</h2><p>${safe((h.roles||[]).map(translateRole).join(" · "))}</p><p>Линия: ${safe((h.lanes||[]).map(translateLane).join(" / ")||"не указана")}</p><p>Сложность и дополнительные параметры будут добавлены после проверки источников.</p><div class="modal-actions"><button id="modal-favorite">${favorites.has(id)?"★ В избранном":"☆ В избранное"}</button><button id="modal-skill-filter">История навыков (${records.length})</button></div></div></div><div class="modal-skills"><h3>СПОСОБНОСТИ</h3>${skills||'<p class="skill-meta">Описания навыков пока отсутствуют.</p>'}</div>${records.length?`<div class="modal-skills"><h3>ЗАПИСИ ПО ПАТЧАМ</h3>${records.map(r=>`<div class="skill-meta">${safe(r.skill_name)} · ${safe(r.patch.version)} · ${safe(sourceBadge(r.verification.status))}</div>`).join("")}</div>`:""}`;
 $("#hero-modal").classList.remove("hidden");
 $("#modal-favorite").onclick=()=>{toggleFavorite(id);$("#modal-favorite").textContent=favorites.has(id)?"★ В избранном":"☆ В избранное"};
 $("#modal-skill-filter").onclick=()=>{closeModal();showView("skills");$("#skill-search").value=id;renderSkills()};
}
function closeModal(){$("#hero-modal").classList.add("hidden")}
function toggleFavorite(id){favorites.has(id)?favorites.delete(id):favorites.add(id);saveFavorites();renderHeroes()}
function showView(view){
 state.view=view;
 $$(".nav-link").forEach(b=>b.classList.toggle("active",b.dataset.view===view));
 ["heroes","items","skills","about"].forEach(v=>$("#"+(v==="heroes"?"database":v+"-view")).classList.toggle("hidden",v!==view));
 $("#hero-toolbar").classList.toggle("hidden",view!=="heroes");
 $("#lane-filters").classList.toggle("hidden",view!=="heroes");
 $("#section-title").innerHTML="ГЕРОИ <span>MLBB</span>";
 if(view==="items")$("#section-title").innerHTML="ПРЕДМЕТЫ <span>MLBB</span>";
 if(view==="skills")$("#section-title").innerHTML="НАВЫКИ <span>ПО ПАТЧАМ</span>";
 if(view==="about")$("#section-title").innerHTML="О <span>ПРОЕКТЕ</span>";
}
function bind(){
 $$(".nav-link").forEach(b=>b.addEventListener("click",()=>{showView(b.dataset.view);$("#main-nav")?.classList.remove("open")}));
 $$("[data-jump]").forEach(b=>b.addEventListener("click",()=>{showView(b.dataset.jump);$("#database").scrollIntoView({behavior:"smooth"})}));
 $("#search").addEventListener("input",e=>{state.query=e.target.value;renderHeroes()});
 $("#role-filters").addEventListener("click",e=>{const b=e.target.closest("[data-role]");if(!b)return;state.role=b.dataset.role;$$("[data-role]").forEach(x=>x.classList.toggle("active",x===b));renderHeroes()});
 $("#lane-filters").addEventListener("click",e=>{const b=e.target.closest("[data-lane]");if(!b)return;state.lane=b.dataset.lane;$$("[data-lane]").forEach(x=>x.classList.toggle("active",x===b));renderHeroes()});
 $("#favorites-toggle").onclick=()=>{state.favoritesOnly=!state.favoritesOnly;$("#favorites-toggle").classList.toggle("active",state.favoritesOnly);$("#favorites-toggle").textContent=state.favoritesOnly?"★":"☆";renderHeroes()};
 $("#hero-grid").addEventListener("click",e=>{const fav=e.target.closest("[data-fav]");if(fav){e.stopPropagation();toggleFavorite(fav.dataset.fav);return}const card=e.target.closest("[data-hero]");if(card)openHero(card.dataset.hero)});
 $("#hero-grid").addEventListener("keydown",e=>{if((e.key==="Enter"||e.key===" ")&&e.target.matches("[data-hero]")){e.preventDefault();openHero(e.target.dataset.hero)}});
 $("#item-search").addEventListener("input",e=>{state.itemQuery=e.target.value;renderItems()});
 $("#item-categories").addEventListener("click",e=>{const b=e.target.closest("[data-category]");if(!b)return;state.itemCategory=b.dataset.category;$$("[data-category]").forEach(x=>x.classList.toggle("active",x===b));renderItems()});
 $("#skill-search").addEventListener("input",renderSkills);$("#patch-filter").addEventListener("change",renderSkills);$("#status-filter").addEventListener("change",renderSkills);
 $("#hero-modal").addEventListener("click",e=>{if(e.target.matches("[data-close-modal]"))closeModal()});
 document.addEventListener("keydown",e=>{if(e.key==="Escape")closeModal();if(e.key==="/"&&!/input|textarea/i.test(document.activeElement.tagName)){e.preventDefault();$("#search").focus()}});
 $("#mobile-menu").onclick=()=>$(".main-nav").classList.toggle("open");
}
bind();
loadData().then(()=>{const patches=[...new Set(DATA.skills.map(x=>x.patch?.version).filter(Boolean))].sort().reverse();patches.forEach(p=>{const o=document.createElement("option");o.value=p;o.textContent=p;$("#patch-filter").append(o)})}).catch(err=>{$("#hero-grid").innerHTML='<div class="empty-state">Не удалось загрузить базу. Обнови страницу чуть позже.</div>';console.error(err)});
