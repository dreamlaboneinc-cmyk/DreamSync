console.log("[DreamSync] dashboard.js booting...");
async function refresh(){
  try{
    const res = await fetch("/api/dashboard",{cache:"no-store"});
    if(!res.ok) throw new Error("API "+res.status);
    const d = await res.json();

    // Usage
    const u = d.usage || {};
    const credits = Number(u.credits_usd||0), spent = Number(u.total_spend_usd||0);
    const pct = Number(u.percent_used||0);   // 0–100
    const bar = pct >= 80 ? "bg-red-600" : "bg-emerald-600";
    document.getElementById("usage").innerHTML =
      `<div class="flex items-center justify-between mb-2">
         <div>OpenAI Spend: <span class="font-semibold">$${spent.toFixed(2)}</span> of $${credits.toFixed(2)}</div>
         <div class="text-sm opacity-80">${pct.toFixed(1)}% used</div>
       </div>
       <div class="w-full h-3 bg-slate-800 rounded">
         <div class="h-3 ${bar} rounded" style="width:${Math.min(100,pct)}%"></div>
       </div>`;

    // Apps
    const apps = (d.apps || d.active_apps || []).map(a => typeof a==="string" ? {alias:a, entry:""} : a);
    document.getElementById("apps").innerHTML = apps.length
      ? apps.map(a => `<li class="flex justify-between"><span>${a.alias}</span><span class="opacity-60 text-xs">${a.entry||""}</span></li>`).join("")
      : "<li class='opacity-70'>No apps</li>";

    // Health
    const m = d.metrics || {};
    const load = (m.loadavg||[]).join(", ");
    const mem = m.mem ? `${(m.mem.used/1e9).toFixed(2)} / ${(m.mem.total/1e9).toFixed(2)} GB` : "n/a";
    document.getElementById("health").textContent =
      `Uptime: ${Math.floor((m.uptime_sec||0)/3600)}h
CPU: ${m.cpu_percent||0}%
Load: ${load}
Mem: ${mem}`;

    // Alerts
    document.getElementById("alerts").textContent = (d.alerts||[]).join("\n") || "No recent alerts.";
  }catch(e){
    console.error("[DreamSync] UI error:", e);
    document.getElementById("alerts").textContent = "UI error: "+e.message;
  }
}
refresh(); setInterval(refresh, 10000);
