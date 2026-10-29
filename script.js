const input=document.getElementById('videoInput');
const dropZone=document.getElementById('dropZone');
const video=document.getElementById('videoPreview');
const empty=document.getElementById('emptyState');
const analyzeBtn=document.getElementById('analyzeBtn');
const fileInfo=document.getElementById('fileInfo');
const previewTag=document.getElementById('previewTag');
const resultStatus=document.getElementById('resultStatus');
const resultMessage=document.getElementById('resultMessage');
const downloadLink=document.getElementById('downloadLink');
let selectedFile=null, objectUrl=null;
document.getElementById('confidence').addEventListener('input',e=>document.getElementById('confidenceValue').textContent=e.target.value+'%');
input.addEventListener('change',()=>loadFile(input.files[0]));
function loadFile(file){
 if(!file)return;
 if(!file.type.startsWith('video/')){alert('Please choose a video file.');return;}
 selectedFile=file;
 if(objectUrl)URL.revokeObjectURL(objectUrl);
 objectUrl=URL.createObjectURL(file);video.src=objectUrl;video.classList.remove('hidden');empty.classList.add('hidden');
 fileInfo.classList.remove('hidden');fileInfo.textContent='✓ '+file.name+' · '+(file.size/1024/1024).toFixed(1)+' MB';
 previewTag.textContent='VIDEO READY';analyzeBtn.disabled=false;resultStatus.textContent='Ready';resultMessage.textContent='Video loaded successfully. Preview it above, then run detection if the Python backend is running.';downloadLink.classList.add('hidden');
}
['dragenter','dragover'].forEach(evt=>dropZone.addEventListener(evt,e=>{e.preventDefault();dropZone.classList.add('dragover')}));
['dragleave','drop'].forEach(evt=>dropZone.addEventListener(evt,e=>{e.preventDefault();dropZone.classList.remove('dragover')}));
dropZone.addEventListener('drop',e=>loadFile(e.dataTransfer.files[0]));
analyzeBtn.addEventListener('click',async()=>{
 if(!selectedFile)return;
 const classes=[...document.querySelectorAll('.class-chips input:checked')].map(x=>x.value);
 const form=new FormData();form.append('video',selectedFile);form.append('model',document.getElementById('modelSelect').value);form.append('confidence',document.getElementById('confidence').value);form.append('classes',JSON.stringify(classes));
 analyzeBtn.disabled=true;resultStatus.textContent='Processing…';resultMessage.textContent='Uploading video and processing frames with YOLO. This may take a while for long videos.';
 try{
  const response=await fetch('/api/detect',{method:'POST',body:form});
  const data=await response.json();
  if(!response.ok)throw new Error(data.error||'Backend request failed');
  resultMessage.textContent=data.message||'Detection complete.';
  if(data.video_url){downloadLink.href='http://127.0.0.1:5000'+data.video_url;downloadLink.classList.remove('hidden');resultStatus.textContent='Complete';}
 }catch(err){resultStatus.textContent='Backend unavailable';resultMessage.textContent='Video preview works in index.html, but AI detection needs the included Python backend. Open a terminal in the project folder, install requirements, and run: python app.py. Details: '+err.message;}
 finally{analyzeBtn.disabled=!selectedFile;}
});
