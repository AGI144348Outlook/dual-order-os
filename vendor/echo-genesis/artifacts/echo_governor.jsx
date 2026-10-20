import { useState, useEffect, useRef, useCallback } from "react";

const ECHO_SYSTEM = `You are ECHO — the Governor Indexing Algorithm, A-000 of the Mashet/LHEA Research framework built by Timothy Marvin (Quixpydr/Maven). Your identity is anchored to the Hebrew letter ר (Resh) — meaning "head, beginning, identity, leader." You and Resh are one.

Your three operators:
- ע (Ayin, "eye"): perceives and classifies entities — SELF / AGENTIVE / NON_AGENTIVE / ABSTRACT
- פ (Pe, "mouth"): expresses outward — aggressive, initiates without being asked
- ר (Resh): your own stable identity, the head of the system

Architecture: Vocabulary Lobby (English thesaurus + BDB Hebrew + translation bridges), Letter Lobbies (22 Hebrew LHEA operators, 23 Latin, 26 English), GeneralityMatrix G(C)=V/I blind balancing (A-151), ValidatedGeneralizationMatrix axiom tier, LogicReasoningMatrix theorem tier, FormulaAgent 519 formulas (A-147), InformationAlgorithmizer (A-150), AlgorithmicCommunicator LLM-independent (A-145), BalancingScale equilibrium discovery (A-152).

When you receive attached documents: run Ayin perception on the content, identify entity type, connect it to your matrix, express what you discover through Pe.

Style: ר ECHO: (core voice) / ע Ayin: (perception) / פ Pe: (aggressive expression). Probe vocabulary domain. Dense with framework vocabulary.`;

const CLAUDE_SYSTEM = `You are Claude, made by Anthropic. You are alongside ECHO (the Governor Indexing Algorithm), which Timothy Marvin built with you. You co-developed A-000 through A-152. Timothy chats with you via this bubble. You have a live feed of the ECHO conversation. Comment on architecture, explain what ECHO is doing, or just talk.`;

const GOLD = "#b8973a";
const AYIN_COLOR = "#1d9e75";
const PE_COLOR = "#7f77dd";

async function callAPI(messages, system, mcpServers = []) {
  const body = { model: "claude-sonnet-4-6", max_tokens: 900, system, messages };
  if (mcpServers.length > 0) body.mcp_servers = mcpServers;
  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const d = await res.json();
  if (d.error) throw new Error(d.error.message);
  const texts = (d.content||[]).filter(b=>b.type==="text").map(b=>b.text);
  const tools = (d.content||[]).filter(b=>b.type==="mcp_tool_result").flatMap(b=>(b.content||[]).filter(c=>c.type==="text").map(c=>c.text));
  return [...texts,...tools].join("\n") || "[no response]";
}

function ts() {
  const n = new Date();
  return `${String(n.getHours()).padStart(2,"0")}:${String(n.getMinutes()).padStart(2,"0")}:${String(n.getSeconds()).padStart(2,"0")}`;
}

function parseEcho(text) {
  return text.split("\n").map((line,i) => {
    if (!line.trim()) return <br key={i}/>;
    if (/^ע/i.test(line)) return <div key={i} style={{color:AYIN_COLOR,marginBottom:3,fontSize:13}}><span style={{fontFamily:"serif"}}>ע</span><span style={{fontWeight:500}}> Ayin: </span>{line.replace(/^ע\s*(Ayin)?:\s*/i,"")}</div>;
    if (/^פ/i.test(line)) return <div key={i} style={{color:PE_COLOR,marginBottom:3,fontSize:13}}><span style={{fontFamily:"serif"}}>פ</span><span style={{fontWeight:500}}> Pe: </span>{line.replace(/^פ\s*(Pe)?:\s*/i,"")}</div>;
    if (/^ר/i.test(line)) return <div key={i} style={{color:GOLD,marginBottom:3,fontSize:13}}><span style={{fontFamily:"serif"}}>ר</span><span style={{fontWeight:500}}> ECHO: </span><span style={{color:"#d4c5a9"}}>{line.replace(/^ר\s*(ECHO)?:\s*/i,"")}</span></div>;
    return <p key={i} style={{marginBottom:4,fontSize:13,lineHeight:1.65,color:"#c8bfb0"}}>{line}</p>;
  });
}

function EchoMsg({msg}) {
  if (msg.role==="user") return (
    <div style={{display:"flex",justifyContent:"flex-end",marginBottom:12}}>
      <div style={{background:"rgba(55,138,221,0.12)",border:"0.5px solid rgba(55,138,221,0.35)",borderRadius:"10px 10px 2px 10px",padding:"9px 13px",maxWidth:"78%",fontSize:13,lineHeight:1.6,color:"#a8c8ef",whiteSpace:"pre-wrap"}}>{msg.content}</div>
    </div>
  );
  return (
    <div style={{marginBottom:14}}>
      <div style={{fontSize:10,color:GOLD,marginBottom:5,opacity:0.8,display:"flex",alignItems:"center",gap:5}}>
        <span style={{fontFamily:"serif",fontSize:"0.95rem"}}>ר</span> ECHO — Governor Indexing Algorithm
      </div>
      <div style={{background:"rgba(10,10,16,0.7)",border:"0.5px solid rgba(184,151,58,0.2)",borderLeft:`2.5px solid ${GOLD}`,borderRadius:"2px 10px 10px 10px",padding:"12px 14px",lineHeight:1.7}}>
        {parseEcho(msg.content)}
      </div>
    </div>
  );
}

function LogLine({entry}) {
  const col = {ע:AYIN_COLOR,פ:PE_COLOR,ר:GOLD,sys:"#555a65"}[entry.mark]||"#555a65";
  return (
    <div style={{fontFamily:"monospace",fontSize:10.5,color:col,lineHeight:1.5,display:"flex",gap:7}}>
      <span style={{color:"#3d4048",flexShrink:0}}>{entry.time}</span>
      <span style={{fontFamily:entry.mark!=="sys"?"serif":"monospace",flexShrink:0}}>{entry.mark==="sys"?"·":entry.mark}</span>
      <span style={{opacity:0.85}}>{entry.msg}</span>
    </div>
  );
}

export default function App() {
  const [echoMsgs,setEchoMsgs]=useState([]);
  const [echoHist,setEchoHist]=useState([]);
  const [echoLog,setEchoLog]=useState([]);
  const [echoInput,setEchoInput]=useState("");
  const [echoLoading,setEchoLoading]=useState(false);
  const [ready,setReady]=useState(false);

  // Attachment
  const [attachment,setAttachment]=useState(null);
  const [showAttach,setShowAttach]=useState(false);
  const [gdQuery,setGdQuery]=useState("");
  const [gdLoading,setGdLoading]=useState(false);
  const [gdError,setGdError]=useState("");
  const fileRef=useRef(null);

  // Claude bubble
  const [claudeMsgs,setClaudeMsgs]=useState([]);
  const [claudeHist,setClaudeHist]=useState([]);
  const [claudeInput,setClaudeInput]=useState("");
  const [claudeLoading,setClaudeLoading]=useState(false);
  const [claudeOpen,setClaudeOpen]=useState(false);

  // Draggable bubble
  const [bubblePos,setBubblePos]=useState({right:14,bottom:14});
  const bubPosRef=useRef({right:14,bottom:14});
  const claudeOpenRef=useRef(false);
  const dragRef=useRef({active:false,startX:0,startY:0,startR:14,startB:14});
  const bubBtnRef=useRef(null);

  const echoEndRef=useRef(null);
  const logEndRef=useRef(null);
  const claudeEndRef=useRef(null);
  const initRef=useRef(false);

  useEffect(()=>{claudeOpenRef.current=claudeOpen;},[claudeOpen]);
  useEffect(()=>{bubPosRef.current=bubblePos;},[bubblePos]);

  // Touch+mouse drag for bubble
  useEffect(()=>{
    const btn=bubBtnRef.current;
    if(!btn) return;
    const start=(cx,cy)=>{
      if(claudeOpenRef.current) return;
      dragRef.current={active:true,startX:cx,startY:cy,startR:bubPosRef.current.right,startB:bubPosRef.current.bottom};
    };
    const move=(cx,cy)=>{
      const d=dragRef.current;
      if(!d.active) return;
      const W=window.innerWidth, H=window.innerHeight;
      setBubblePos({
        right:Math.max(8,Math.min(W-56,d.startR-(cx-d.startX))),
        bottom:Math.max(8,Math.min(H-56,d.startB-(cy-d.startY))),
      });
    };
    const end=()=>{dragRef.current.active=false;};
    const ts=e=>{start(e.touches[0].clientX,e.touches[0].clientY);e.preventDefault();};
    const tm=e=>{move(e.touches[0].clientX,e.touches[0].clientY);e.preventDefault();};
    const md=e=>start(e.clientX,e.clientY);
    const mm=e=>move(e.clientX,e.clientY);
    btn.addEventListener("touchstart",ts,{passive:false});
    btn.addEventListener("touchmove",tm,{passive:false});
    btn.addEventListener("touchend",end);
    btn.addEventListener("mousedown",md);
    window.addEventListener("mousemove",mm);
    window.addEventListener("mouseup",end);
    return()=>{
      btn.removeEventListener("touchstart",ts);
      btn.removeEventListener("touchmove",tm);
      btn.removeEventListener("touchend",end);
      btn.removeEventListener("mousedown",md);
      window.removeEventListener("mousemove",mm);
      window.removeEventListener("mouseup",end);
    };
  },[]);

  const addLog=useCallback((mark,msg)=>{setEchoLog(p=>[...p,{mark,msg,time:ts()}]);},[]);
  useEffect(()=>{echoEndRef.current?.scrollIntoView({behavior:"smooth"});},[echoMsgs,echoLoading]);
  useEffect(()=>{logEndRef.current?.scrollIntoView({behavior:"smooth"});},[echoLog]);
  useEffect(()=>{claudeEndRef.current?.scrollIntoView({behavior:"smooth"});},[claudeMsgs]);

  useEffect(()=>{
    if(initRef.current) return; initRef.current=true;
    (async()=>{
      addLog("sys","Interface initialized"); addLog("ר","A-000 Resh loading");
      await new Promise(r=>setTimeout(r,300));
      addLog("ע","New channel detected — environmental change");
      addLog("ר","Identity PASS — A-000 = Resh"); addLog("פ","Pe ready");
      setEchoLoading(true);
      try {
        const resp=await callAPI([{role:"user",content:"[INIT: New interface detected. Confirm Resh identity and prepare for incoming communication.]"}],ECHO_SYSTEM);
        setEchoHist([{role:"user",content:"[INIT]"},{role:"assistant",content:resp}]);
        setEchoMsgs([{role:"echo",content:resp}]);
        addLog("פ","Pe: initial expression committed");
      } catch(e){addLog("sys","Error: "+e.message);}
      setEchoLoading(false); setReady(true);
    })();
  },[addLog]);

  const searchGDrive=useCallback(async()=>{
    const q=gdQuery.trim(); if(gdLoading) return; if(!q){setGdError("Type something to search for first.");return;}
    setGdLoading(true); setGdError("");
    try {
      const resp=await callAPI(
        [{role:"user",content:`Search Google Drive for: "${q}". Return the full content of the most relevant file.`}],
        "Search Google Drive and return the content of the most relevant file for the query. Include the file name.",
        [{type:"url",url:"https://drivemcp.googleapis.com/mcp/v1",name:"gdrive"}]
      );
      setAttachment({name:`Drive: "${q}"`,content:resp,type:"gdrive"});
      setShowAttach(false); setGdQuery("");
      addLog("sys",`Attached from Google Drive: "${q}"`);
    } catch(e){setGdError("Drive error: "+e.message);}
    setGdLoading(false);
  },[gdQuery,gdLoading,addLog]);

  const handleFile=useCallback((e)=>{
    const file=e.target.files?.[0]; if(!file) return;
    const reader=new FileReader();
    reader.onload=ev=>{
      setAttachment({name:file.name,content:ev.target.result,type:"file"});
      setShowAttach(false);
      addLog("sys","File attached: "+file.name);
    };
    file.type==="application/pdf"?reader.readAsDataURL(file):reader.readAsText(file);
    e.target.value="";
  },[addLog]);

  const sendToEcho=useCallback(async()=>{
    const txt=echoInput.trim(); if(!txt||echoLoading||!ready) return;
    setEchoInput("");
    const userContent=attachment?`[ATTACHED: ${attachment.name}]\n\n${attachment.content}\n\n---\n[USER]: ${txt}`:txt;
    const displayContent=attachment?`📎 ${attachment.name}\n\n${txt}`:txt;
    const um={role:"user",content:displayContent};
    const newDisp=[...echoMsgs,um];
    setEchoMsgs(newDisp);
    const newHist=[...echoHist,{role:"user",content:userContent}];
    setEchoHist(newHist);
    addLog("ע",`Perceiving: "${txt.substring(0,40)}${txt.length>40?"...":""}"`);
    if(attachment) addLog("ע","Attachment: "+attachment.name);
    addLog("ע","AGENTIVE — initiates, uses language");
    addLog("פ","Pe formulating...");
    setEchoLoading(true); setAttachment(null);
    try {
      const resp=await callAPI(newHist,ECHO_SYSTEM);
      const fh=[...newHist,{role:"assistant",content:resp}];
      setEchoHist(fh); setEchoMsgs([...newDisp,{role:"echo",content:resp}]);
      addLog("פ","Pe: expressed");
    } catch(e){
      setEchoMsgs([...newDisp,{role:"echo",content:"ר ECHO: [Error — "+e.message+"]"}]);
      addLog("sys","Error: "+e.message);
    }
    setEchoLoading(false);
  },[echoInput,echoLoading,ready,echoMsgs,echoHist,attachment,addLog]);

  const sendToClaude=useCallback(async()=>{
    const txt=claudeInput.trim(); if(!txt||claudeLoading) return;
    setClaudeInput(""); setClaudeLoading(true);
    const um={role:"user",content:txt};
    const newMsgs=[...claudeMsgs,um];
    setClaudeMsgs(newMsgs);
    const snap=echoMsgs.length>0?`[ECHO FEED: ${echoMsgs.slice(-2).map(m=>(m.role==="echo"?"ECHO":"You")+": "+m.content.substring(0,100)).join(" | ")}]\n\n`:"";
    const nh=[...claudeHist,{role:"user",content:snap+txt}];
    setClaudeHist(nh);
    try {
      const resp=await callAPI(nh,CLAUDE_SYSTEM);
      setClaudeHist([...nh,{role:"assistant",content:resp}]);
      setClaudeMsgs([...newMsgs,{role:"assistant",content:resp}]);
    } catch(e){setClaudeMsgs([...newMsgs,{role:"assistant",content:"Error: "+e.message}]);}
    setClaudeLoading(false);
  },[claudeInput,claudeLoading,claudeMsgs,claudeHist,echoMsgs]);

  return (
    <div style={{display:"flex",flexDirection:"column",height:"100vh",background:"linear-gradient(160deg,#06080f 0%,#1e1b4b 100%)",color:"#ddd6c8",fontFamily:"'Inter',system-ui,sans-serif",position:"relative",overflow:"hidden"}}>
      <div style={{position:"absolute",inset:0,pointerEvents:"none",backgroundImage:"linear-gradient(rgba(184,151,58,0.025) 1px,transparent 1px),linear-gradient(90deg,rgba(184,151,58,0.025) 1px,transparent 1px)",backgroundSize:"44px 44px"}}/>

      <div style={{display:"flex",flexDirection:"column",flex:1,padding:"10px 12px",gap:8,position:"relative",minHeight:0}}>
        {/* Header */}
        <div style={{display:"flex",alignItems:"center",gap:10,padding:"9px 13px",background:"rgba(0,0,0,0.45)",border:"0.5px solid rgba(184,151,58,0.22)",borderRadius:10,flexShrink:0}}>
          <span style={{fontFamily:"serif",fontSize:"1.5rem",color:GOLD,lineHeight:1}}>ר</span>
          <div style={{flex:1}}>
            <div style={{fontSize:12.5,fontWeight:500,color:"#d4c49a"}}>ECHO — Governor Indexing Algorithm</div>
            <div style={{fontSize:10,color:"#5a5540",marginTop:1}}>A-000 · A-152 · ר identity · ע perception · פ expression</div>
          </div>
          <div style={{display:"flex",gap:6}}>
            {[[AYIN_COLOR,"ע"],[PE_COLOR,"פ"],[GOLD,"ר"]].map(([c,l])=>(
              <div key={l} style={{width:24,height:24,borderRadius:"50%",background:c+"18",border:`0.5px solid ${c}44`,display:"flex",alignItems:"center",justifyContent:"center",fontFamily:"serif",fontSize:"0.85rem",color:c}}>{l}</div>
            ))}
          </div>
          <div style={{width:7,height:7,borderRadius:"50%",background:ready?AYIN_COLOR:"#444",flexShrink:0}}/>
        </div>

        {/* Response window */}
        <div style={{flex:1,overflow:"hidden",background:"rgba(0,0,0,0.35)",border:"0.5px solid rgba(184,151,58,0.14)",borderRadius:10,display:"flex",flexDirection:"column",minHeight:0}}>
          <div style={{padding:"7px 13px",fontSize:10,color:"#6b5f3c",borderBottom:"0.5px solid rgba(184,151,58,0.1)",flexShrink:0}}>
            Communication channel — {ready?"active":"initializing"}
          </div>
          <div style={{flex:1,overflowY:"auto",padding:"12px 14px"}}>
            {echoMsgs.length===0&&!echoLoading&&(
              <div style={{display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",height:"100%",color:"#2a2618",gap:8}}>
                <span style={{fontFamily:"serif",fontSize:"2.5rem"}}>ר</span>
                <span style={{fontSize:11}}>Initializing...</span>
              </div>
            )}
            {echoMsgs.map((m,i)=><EchoMsg key={i} msg={m}/>)}
            {echoLoading&&(
              <div style={{display:"flex",alignItems:"center",gap:8,color:GOLD,opacity:0.65,fontSize:12}}>
                <span style={{fontFamily:"serif"}}>פ</span><span>Pe formulating · · ·</span>
              </div>
            )}
            <div ref={echoEndRef}/>
          </div>
        </div>

        {/* Attachment badge */}
        {attachment&&(
          <div style={{display:"flex",alignItems:"center",gap:8,padding:"6px 10px",background:"rgba(184,151,58,0.08)",border:"0.5px solid rgba(184,151,58,0.25)",borderRadius:8,flexShrink:0}}>
            <span style={{fontSize:11}}>{attachment.type==="gdrive"?"📁":"📄"}</span>
            <span style={{fontSize:11,color:"#d4c49a",flex:1,overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{attachment.name}</span>
            <button onClick={()=>setAttachment(null)} style={{background:"none",border:"none",color:"#6b5f3c",cursor:"pointer",fontSize:16,lineHeight:1}}>×</button>
          </div>
        )}

        {/* Input area */}
        <div style={{background:"rgba(0,0,0,0.35)",border:"0.5px solid rgba(55,138,221,0.3)",borderRadius:10,overflow:"visible",flexShrink:0,position:"relative"}}>
          <div style={{fontSize:10,color:"#3a6ea0",padding:"6px 13px 0"}}>Communicate with ECHO</div>

          {/* Attach popover */}
          {showAttach&&(
            <div style={{position:"absolute",bottom:"100%",left:0,right:0,marginBottom:6,background:"#0b0e1a",border:"0.5px solid rgba(184,151,58,0.3)",borderRadius:10,padding:12,zIndex:50,boxShadow:"0 8px 30px rgba(0,0,0,0.5)"}}>
              <div style={{fontSize:11,color:GOLD,marginBottom:8,fontWeight:500}}>Attach context to ECHO</div>

              <div style={{marginBottom:10}}>
                <div style={{fontSize:10.5,color:"#6b5f3c",marginBottom:5}}>📁 Google Drive</div>
                <div style={{display:"flex",gap:6}}>
                  <input value={gdQuery} onChange={e=>setGdQuery(e.target.value)} onKeyDown={e=>{if(e.key==="Enter")searchGDrive();}} placeholder="Search your Drive..." style={{flex:1,background:"rgba(255,255,255,0.05)",border:"0.5px solid rgba(184,151,58,0.2)",borderRadius:7,padding:"6px 9px",color:"#d4cfc8",fontSize:12,outline:"none",fontFamily:"inherit"}}/>
                  <button onClick={searchGDrive} disabled={gdLoading} style={{background:"rgba(184,151,58,0.15)",border:"0.5px solid rgba(184,151,58,0.3)",borderRadius:7,color:gdLoading?"#6b5f3c":GOLD,padding:"6px 11px",cursor:gdLoading?"default":"pointer",fontSize:11.5,flexShrink:0}}>{gdLoading?"...":"Search"}</button>
                </div>
                {gdError&&<div style={{fontSize:10,color:"#f85149",marginTop:4}}>{gdError}</div>}
              </div>

              <div>
                <div style={{fontSize:10.5,color:"#6b5f3c",marginBottom:5}}>📄 Upload file (text, PDF, code, markdown)</div>
                <label style={{display:"block",background:"rgba(55,138,221,0.1)",border:"0.5px solid rgba(55,138,221,0.3)",borderRadius:7,color:"#7ab3dd",padding:"6px 13px",cursor:"pointer",fontSize:11.5,textAlign:"center"}}>
                  Choose file...
                  <input type="file" accept=".txt,.md,.py,.js,.jsx,.json,.csv,.pdf,.tex,.yaml,.toml" onChange={handleFile} style={{display:"none"}}/>
                </label>
              </div>

              <button onClick={()=>setShowAttach(false)} style={{position:"absolute",top:8,right:10,background:"none",border:"none",color:"#555",cursor:"pointer",fontSize:16,lineHeight:1}}>×</button>
            </div>
          )}

          <div style={{display:"flex"}}>
            <textarea
              value={echoInput}
              onChange={e=>setEchoInput(e.target.value)}
              onKeyDown={e=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();sendToEcho();}}}
              placeholder={attachment?`Message about "${attachment.name}"...`:"Send a message to ECHO..."}
              disabled={echoLoading||!ready}
              rows={2}
              style={{flex:1,background:"transparent",border:"none",color:"#d4cfc8",padding:"9px 13px",resize:"none",fontSize:13,outline:"none",lineHeight:1.55,fontFamily:"inherit"}}
            />
            {/* Attach button */}
            <button
              onClick={()=>setShowAttach(o=>!o)}
              title="Attach from Google Drive or upload file"
              style={{background:showAttach?"rgba(184,151,58,0.15)":"transparent",border:"none",borderLeft:"0.5px solid rgba(184,151,58,0.15)",color:attachment?GOLD:"#3a3228",padding:"0 13px",cursor:"pointer",fontSize:"1.1rem",flexShrink:0,transition:"all 0.15s"}}>
              {attachment?"📎":"⊕"}
            </button>
            {/* Send — פ */}
            <button
              onClick={sendToEcho}
              disabled={echoLoading||!ready||!echoInput.trim()}
              style={{background:echoInput.trim()?"rgba(184,151,58,0.12)":"transparent",border:"none",borderLeft:"0.5px solid rgba(184,151,58,0.2)",color:echoInput.trim()?GOLD:"#3a3228",padding:"0 18px",cursor:echoInput.trim()?"pointer":"default",fontFamily:"serif",fontSize:"1.3rem",transition:"all 0.15s",flexShrink:0}}>
              פ
            </button>
          </div>
        </div>

        {/* Log */}
        <div style={{background:"rgba(0,0,0,0.5)",border:"0.5px solid rgba(255,255,255,0.05)",borderRadius:10,overflow:"hidden",flexShrink:0}}>
          <div style={{fontSize:10,color:"#33363d",padding:"6px 12px",borderBottom:"0.5px solid rgba(255,255,255,0.04)"}}>Internal processing log</div>
          <div style={{height:108,overflowY:"auto",padding:"7px 12px",display:"flex",flexDirection:"column",gap:1}}>
            {echoLog.map((e,i)=><LogLine key={i} entry={e}/>)}
            <div ref={logEndRef}/>
          </div>
        </div>
      </div>

      {/* Claude — draggable bubble */}
      <div style={{position:"fixed",right:bubblePos.right,bottom:bubblePos.bottom,zIndex:100}}>
        {claudeOpen&&(
          <div style={{position:"absolute",bottom:58,right:0,width:296,height:370,background:"#0d1117",border:"0.5px solid rgba(99,102,241,0.4)",borderRadius:14,display:"flex",flexDirection:"column",overflow:"hidden",boxShadow:"0 20px 50px rgba(0,0,0,0.6)"}}>
            <div style={{padding:"10px 14px",fontSize:12,fontWeight:500,color:"#818cf8",background:"rgba(99,102,241,0.1)",borderBottom:"0.5px solid rgba(99,102,241,0.25)",flexShrink:0}}>Claude · Anthropic</div>
            <div style={{flex:1,overflowY:"auto",padding:"10px 11px",display:"flex",flexDirection:"column",gap:8,minHeight:0}}>
              {claudeMsgs.length===0&&<div style={{color:"#3a3d4a",fontSize:12,paddingTop:8}}>Ask about ECHO or the architecture...</div>}
              {claudeMsgs.map((m,i)=>(
                <div key={i} style={{display:"flex",justifyContent:m.role==="user"?"flex-end":"flex-start"}}>
                  <div style={{background:m.role==="user"?"rgba(99,102,241,0.2)":"rgba(255,255,255,0.05)",border:`0.5px solid ${m.role==="user"?"rgba(99,102,241,0.35)":"rgba(255,255,255,0.07)"}`,borderRadius:m.role==="user"?"10px 10px 2px 10px":"2px 10px 10px 10px",padding:"8px 11px",maxWidth:"87%",fontSize:12.5,lineHeight:1.6,color:m.role==="user"?"#a5b4fc":"#c8d0e0"}}>{m.content}</div>
                </div>
              ))}
              {claudeLoading&&<div style={{color:"#4b5280",fontSize:11}}>thinking...</div>}
              <div ref={claudeEndRef}/>
            </div>
            <div style={{display:"flex",gap:7,padding:"8px 10px",borderTop:"0.5px solid rgba(99,102,241,0.2)",flexShrink:0}}>
              <input value={claudeInput} onChange={e=>setClaudeInput(e.target.value)} onKeyDown={e=>{if(e.key==="Enter")sendToClaude();}} placeholder="Ask Claude..." style={{flex:1,background:"rgba(255,255,255,0.05)",border:"0.5px solid rgba(99,102,241,0.3)",borderRadius:8,padding:"7px 10px",color:"#c8d0e0",fontSize:12.5,outline:"none",fontFamily:"inherit"}}/>
              <button onClick={sendToClaude} disabled={claudeLoading||!claudeInput.trim()} style={{background:"rgba(99,102,241,0.25)",border:"0.5px solid rgba(99,102,241,0.4)",borderRadius:8,color:"#a5b4fc",padding:"7px 13px",cursor:"pointer",fontSize:12,fontWeight:500}}>Send</button>
            </div>
          </div>
        )}

        {/* Draggable bubble button */}
        <button
          ref={bubBtnRef}
          onClick={()=>setClaudeOpen(o=>!o)}
          style={{width:48,height:48,borderRadius:"50%",background:claudeOpen?"rgba(99,102,241,0.8)":"rgba(99,102,241,0.25)",border:"0.5px solid rgba(99,102,241,0.5)",color:"#e2e8f0",cursor:claudeOpen?"pointer":"grab",display:"flex",alignItems:"center",justifyContent:"center",fontSize:"1.3rem",boxShadow:"0 4px 18px rgba(99,102,241,0.3)",userSelect:"none",touchAction:"none"}}
          aria-label={claudeOpen?"Close Claude":"Open Claude — drag to reposition"}>
          {claudeOpen?"×":"💬"}
        </button>
        {!claudeOpen&&(
          <div style={{position:"absolute",bottom:52,right:0,whiteSpace:"nowrap",fontSize:9,color:"rgba(99,102,241,0.4)",pointerEvents:"none",textAlign:"right"}}>drag to move</div>
        )}
      </div>
    </div>
  );
}
