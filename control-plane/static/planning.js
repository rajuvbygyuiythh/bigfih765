'use strict';
const byId=id=>document.getElementById(id);
let token='', authorized=false, busy=false, disposed=false;
window.addEventListener('pagehide',()=>{disposed=true;token='';});
async function get(path){
  const response=await fetch(path,{headers:token?{Authorization:'Bearer '+token}:{}});
  if(!response.ok)throw new Error(response.status===401?'Operator token required.':'Saved workflow unavailable; locks remain enforced.');
  return response.json();
}
async function refresh(){
  if(busy||disposed)return;busy=true;
  try{
    const state=await get('/api/workflow');if(disposed)return;
    if(!Array.isArray(state.order)||!state.sites)throw new Error('Invalid workflow; no progress inferred.');
    const rows=state.order.map((id,index)=>{
      const site=state.sites[id];
      if(!site||!Array.isArray(site.completed_steps)||!['active','locked','done'].includes(site.state))throw new Error('Invalid workflow; no progress inferred.');
      const row=document.createElement('tr');
      for(const value of [index+1,id,site.state.toUpperCase(),`${site.completed_steps.length}/8`,`${site.percent}%`]){
        const cell=document.createElement('td');cell.textContent=String(value);row.append(cell);
      }
      return row;
    });
    byId('plan-queue').replaceChildren(...rows);authorized=true;byId('plan-auth').hidden=true;
    byId('plan-status').textContent=`Active: ${state.active_site||'none'} · ${state.order.filter(id=>state.sites[id].state==='locked').length} locked · saved workflow only, no provider probe`;
  }catch(error){if(!disposed){authorized=false;byId('plan-queue').replaceChildren();byId('plan-auth').hidden=false;byId('plan-status').textContent=error.message;}}
  finally{busy=false;}
}
byId('plan-auth').onsubmit=async event=>{event.preventDefault();if(busy)return;token=byId('plan-token').value;byId('plan-token').value='';await refresh();if(!authorized)token='';};
(async()=>{try{const info=await get('/api/info');if(disposed)return;if(info.auth_required){byId('plan-auth').hidden=false;byId('plan-status').textContent='Authenticate to read the actual locked queue.';}else await refresh();}catch(error){if(!disposed)byId('plan-status').textContent=error.message;}})();
setInterval(()=>{if(authorized&&!disposed)refresh();},15000);
