import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from pydantic import BaseModel
from src.engine import RobustAnonymizationEngine

app = FastAPI(docs_url=None, redoc_url=None)

STORAGE_DIR = os.path.abspath("./storage_vault")
os.makedirs(STORAGE_DIR, exist_ok=True)

class TextAnonymizeRequest(BaseModel):
    text: str

class TextRehydrateRequest(BaseModel):
    sanitized_text: str
    encrypted_vault: str

class TextTranslateRequest(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    return """
<!DOCTYPE html>
<html lang="fr" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Microservice — Passerelle Souveraine LLM</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        brand: {
                            50: '#faf5ff',
                            400: '#c084fc',
                            500: '#a855f7',
                            600: '#9333ea',
                            700: '#7e22ce'
                        }
                    }
                }
            }
        }
    </script>
    <style>
        body {
            font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
            background-color: #070709;
        }
        .code-font {
            font-family: 'JetBrains Mono', monospace;
        }
        .glow-border {
            border: 1px solid rgba(168, 85, 247, 0.22);
            box-shadow: 0 0 25px rgba(168, 85, 247, 0.06);
        }
        .glow-border-hover:hover {
            border-color: rgba(192, 132, 252, 0.45);
            box-shadow: 0 0 30px rgba(168, 85, 247, 0.15);
        }
    </style>
</head>
<body class="text-zinc-100 antialiased min-h-screen flex flex-col justify-between selection:bg-brand-500 selection:text-white">

    <header class="border-b border-zinc-800/80 bg-[#0B0B0E]/80 backdrop-blur-xl sticky top-0 z-50">
        <div class="max-w-4xl mx-auto px-6 h-16 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="w-8 h-8 rounded-lg bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center text-white font-bold text-sm shadow-[0_0_15px_rgba(168,85,247,0.4)]">
                    μS
                </div>
                <div>
                    <h1 class="text-xs font-semibold tracking-wider uppercase text-zinc-400">Microservice</h1>
                    <p class="text-sm font-medium text-white">Passerelle Relation Client & LLM</p>
                </div>
            </div>
            <div class="flex items-center space-x-2 bg-zinc-900/80 px-3 py-1.5 rounded-full border border-zinc-800">
                <span class="w-2 h-2 rounded-full bg-brand-500 animate-pulse"></span>
                <span class="text-xs font-medium text-zinc-300">Actif</span>
            </div>
        </div>
    </header>

    <main class="max-w-4xl mx-auto px-6 py-10 flex-1 w-full space-y-6">
        
        <div class="flex justify-center">
            <div class="flex p-1 bg-zinc-900/90 rounded-xl border border-zinc-800 text-xs font-medium">
                <button id="tabTextBtn" type="button" class="px-6 py-2 rounded-lg bg-brand-600 text-white font-semibold transition-all shadow-[0_0_12px_rgba(147,51,234,0.3)]">
                    Flux Direct
                </button>
                <button id="tabPdfBtn" type="button" class="px-6 py-2 rounded-lg text-zinc-400 hover:text-white transition-all">
                    Document PDF
                </button>
            </div>
        </div>

        <!-- FLUX DIRECT -->
        <div id="sectionText" class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                
                <div class="bg-[#0D0D12] rounded-2xl p-5 glow-border flex flex-col justify-between space-y-4">
                    <div class="space-y-2">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-semibold uppercase tracking-wider text-zinc-400">Entrée Source</span>
                            <button id="clearTextBtn" class="text-[11px] text-zinc-500 hover:text-zinc-300">Effacer</button>
                        </div>
                        <textarea id="rawTextInput" rows="8" placeholder="Saisissez ou collez ici la communication..." class="w-full text-xs p-3.5 rounded-xl border border-zinc-800/80 bg-zinc-950/60 focus:border-brand-500 focus:outline-none text-zinc-200 placeholder-zinc-600 resize-none transition-all leading-relaxed"></textarea>
                    </div>
                    <button id="processTextBtn" type="button" class="w-full py-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 text-white text-xs font-semibold hover:opacity-95 transition-all shadow-[0_0_20px_rgba(168,85,247,0.25)] flex items-center justify-center space-x-2">
                        <span>Sécuriser le contenu</span>
                    </button>
                </div>

                <div class="bg-[#0D0D12] rounded-2xl p-5 glow-border flex flex-col justify-between space-y-4">
                    <div class="space-y-2">
                        <div class="flex items-center justify-between">
                            <div class="flex items-center space-x-2">
                                <span class="text-xs font-semibold uppercase tracking-wider text-brand-400">Sortie Protégée</span>
                                <span id="badgeCount" class="hidden text-[10px] px-2 py-0.5 rounded-full bg-brand-500/10 text-brand-400 border border-brand-500/20 font-mono">0 entité</span>
                            </div>
                            <button id="copyBtn" class="text-[11px] text-brand-400 hover:text-brand-300 transition-colors">Copier</button>
                        </div>
                        <div id="sanitizedTextOutput" class="h-[188px] text-xs p-3.5 rounded-xl bg-zinc-950/60 border border-zinc-800/80 text-zinc-300 code-font whitespace-pre-wrap overflow-y-auto leading-relaxed">
                            <span class="text-zinc-600 italic">Le contenu neutralisé apparaîtra ici...</span>
                        </div>
                    </div>
                    <button id="triggerRestoreBtn" type="button" class="w-full py-2.5 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-brand-500/50 text-zinc-300 hover:text-white text-xs font-semibold transition-all">
                        Restitution locale
                    </button>
                </div>
            </div>

            <div id="rehydrateBlock" class="hidden bg-[#0D0D12] rounded-2xl p-5 border border-emerald-500/20 shadow-[0_0_20px_rgba(16,185,129,0.04)] space-y-3">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-2">
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                        <span class="text-xs font-semibold text-emerald-400 uppercase tracking-wider">Contenu Reconstitué</span>
                    </div>
                    <span class="text-[11px] text-zinc-500">Validation d'intégrité terminée</span>
                </div>
                <div id="restoredOutput" class="text-xs p-4 rounded-xl bg-zinc-950/80 border border-zinc-800/60 text-zinc-200 whitespace-pre-wrap leading-relaxed"></div>
            </div>
        </div>

        <!-- DOCUMENT PDF -->
        <div id="sectionPdf" class="hidden space-y-6">
            <div class="bg-[#0D0D12] rounded-2xl p-8 glow-border space-y-6">
                
                <input type="file" id="fileInput" class="hidden" accept=".pdf">

                <div id="dropZone" class="border border-dashed border-zinc-800 hover:border-brand-500/60 rounded-xl p-12 text-center cursor-pointer transition-all bg-zinc-950/40 glow-border-hover group">
                    <div class="space-y-3">
                        <div class="w-12 h-12 rounded-xl bg-zinc-900 group-hover:bg-brand-500/10 border border-zinc-800 group-hover:border-brand-500/30 flex items-center justify-center mx-auto transition-all">
                            <svg class="w-5 h-5 text-zinc-400 group-hover:text-brand-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                            </svg>
                        </div>
                        <div class="space-y-1">
                            <div class="text-xs font-semibold text-zinc-200">Sélectionner ou glisser un fichier PDF</div>
                            <div class="text-[11px] text-zinc-500">Biffure vectorielle sans rétention</div>
                        </div>
                    </div>
                </div>

                <div id="loaderPdf" class="hidden text-center py-6 space-y-2">
                    <div class="w-6 h-6 border-2 border-brand-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
                    <span class="text-xs text-zinc-400">Génération du document sécurisé...</span>
                </div>

                <div id="fileCard" class="hidden border border-zinc-800/80 rounded-xl p-5 bg-zinc-950/60 space-y-4">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center space-x-3 overflow-hidden">
                            <div class="w-9 h-9 rounded-lg bg-brand-500/10 border border-brand-500/20 flex items-center justify-center text-[10px] font-bold text-brand-400 shrink-0">
                                PDF
                            </div>
                            <div class="truncate">
                                <div id="fileName" class="text-xs font-semibold text-zinc-200 truncate">document.pdf</div>
                                <div class="text-[11px] text-emerald-400 flex items-center space-x-1.5">
                                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                                    <span>Prêt pour transmission</span>
                                </div>
                            </div>
                        </div>
                        <a id="downloadBtn" href="#" class="shrink-0 px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold transition-all shadow-[0_0_15px_rgba(168,85,247,0.3)]">
                            Télécharger
                        </a>
                    </div>

                    <div class="pt-3 border-t border-zinc-800/80 flex items-center justify-between text-xs">
                        <button id="replaceBtn" type="button" class="text-brand-400 hover:text-brand-300 font-medium">
                            Remplacer le fichier
                        </button>
                        <button id="deleteBtn" type="button" class="text-zinc-500 hover:text-rose-400 font-medium transition-colors">
                            Supprimer
                        </button>
                    </div>
                </div>

            </div>
        </div>

    </main>

    <footer class="border-t border-zinc-800/50 py-4 bg-[#070709]">
        <div class="max-w-4xl mx-auto px-6 flex items-center justify-between text-[11px] text-zinc-500">
            <span>Passerelle Cryptographique Souveraine</span>
            <span>Protocole AES-256-GCM</span>
        </div>
    </footer>

    <script>
        const tabTextBtn = document.getElementById('tabTextBtn');
        const tabPdfBtn = document.getElementById('tabPdfBtn');
        const sectionText = document.getElementById('sectionText');
        const sectionPdf = document.getElementById('sectionPdf');

        tabTextBtn.addEventListener('click', () => {
            tabTextBtn.className = "px-6 py-2 rounded-lg bg-brand-600 text-white font-semibold transition-all shadow-[0_0_12px_rgba(147,51,234,0.3)]";
            tabPdfBtn.className = "px-6 py-2 rounded-lg text-zinc-400 hover:text-white transition-all";
            sectionText.classList.remove('hidden');
            sectionPdf.classList.add('hidden');
        });

        tabPdfBtn.addEventListener('click', () => {
            tabPdfBtn.className = "px-6 py-2 rounded-lg bg-brand-600 text-white font-semibold transition-all shadow-[0_0_12px_rgba(147,51,234,0.3)]";
            tabTextBtn.className = "px-6 py-2 rounded-lg text-zinc-400 hover:text-white transition-all";
            sectionPdf.classList.remove('hidden');
            sectionText.classList.add('hidden');
        });

        let currentVaultPayload = null;
        const rawTextInput = document.getElementById('rawTextInput');
        const processTextBtn = document.getElementById('processTextBtn');
        const sanitizedTextOutput = document.getElementById('sanitizedTextOutput');
        const badgeCount = document.getElementById('badgeCount');
        const copyBtn = document.getElementById('copyBtn');
        const triggerRestoreBtn = document.getElementById('triggerRestoreBtn');
        const rehydrateBlock = document.getElementById('rehydrateBlock');
        const restoredOutput = document.getElementById('restoredOutput');
        const clearTextBtn = document.getElementById('clearTextBtn');

        clearTextBtn.addEventListener('click', () => {
            rawTextInput.value = '';
            sanitizedTextOutput.innerHTML = '<span class="text-zinc-600 italic">Le contenu neutralisé apparaîtra ici...</span>';
            badgeCount.classList.add('hidden');
            rehydrateBlock.classList.add('hidden');
            currentVaultPayload = null;
        });

        processTextBtn.addEventListener('click', async () => {
            const content = rawTextInput.value.trim();
            if (!content) return;

            processTextBtn.disabled = true;
            processTextBtn.innerText = "Traitement en cours...";

            try {
                const res = await fetch("/api/v1/sanitize-text", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ text: content })
                });
                const data = await res.json();

                sanitizedTextOutput.textContent = data.sanitized_text;
                currentVaultPayload = data.encrypted_vault;

                badgeCount.textContent = `${data.entities_count} élément(s) neutralisé(s)`;
                badgeCount.classList.remove('hidden');
                rehydrateBlock.classList.add('hidden');
            } catch (err) {
                alert("Erreur lors de la sécurisation");
            } finally {
                processTextBtn.disabled = false;
                processTextBtn.innerText = "Sécuriser le contenu";
            }
        });

        copyBtn.addEventListener('click', () => {
            if (!sanitizedTextOutput.textContent) return;
            navigator.clipboard.writeText(sanitizedTextOutput.textContent);
            copyBtn.textContent = "Copié";
            setTimeout(() => copyBtn.textContent = "Copier", 1800);
        });

        triggerRestoreBtn.addEventListener('click', async () => {
            if (!currentVaultPayload || !sanitizedTextOutput.textContent) return;

            triggerRestoreBtn.disabled = true;
            try {
                const res = await fetch("/api/v1/rehydrate-text", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        sanitized_text: sanitizedTextOutput.textContent,
                        encrypted_vault: currentVaultPayload
                    })
                });
                const data = await res.json();
                restoredOutput.textContent = data.restored_text;
                rehydrateBlock.classList.remove('hidden');
            } catch (err) {
                alert("Erreur de restitution");
            } finally {
                triggerRestoreBtn.disabled = false;
            }
        });

        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        const loaderPdf = document.getElementById('loaderPdf');
        const fileCard = document.getElementById('fileCard');
        const fileName = document.getElementById('fileName');
        const downloadBtn = document.getElementById('downloadBtn');
        const replaceBtn = document.getElementById('replaceBtn');
        const deleteBtn = document.getElementById('deleteBtn');

        let serverFilename = null;

        dropZone.addEventListener('click', () => fileInput.click());
        replaceBtn.addEventListener('click', () => fileInput.click());

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length) uploadPdf(e.target.files[0]);
        });

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('border-brand-500');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('border-brand-500');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('border-brand-500');
            if (e.dataTransfer.files.length) uploadPdf(e.dataTransfer.files[0]);
        });

        deleteBtn.addEventListener('click', async () => {
            if (!serverFilename) return;
            try {
                await fetch(`/api/v1/delete/${serverFilename}`, { method: 'DELETE' });
            } catch (err) {
                console.error(err);
            }
            resetPdfUI();
        });

        function resetPdfUI() {
            fileInput.value = '';
            serverFilename = null;
            fileCard.classList.add('hidden');
            dropZone.classList.remove('hidden');
        }

        async function uploadPdf(file) {
            dropZone.classList.add('hidden');
            fileCard.classList.add('hidden');
            loaderPdf.classList.remove('hidden');

            const formData = new FormData();
            formData.append("file", file);

            try {
                const res = await fetch("/api/v1/sanitize", { method: "POST", body: formData });
                const data = await res.json();

                if (!res.ok) throw new Error(data.detail || "Erreur de traitement");

                serverFilename = data.filename;
                fileName.textContent = file.name;
                downloadBtn.href = data.download_url;

                loaderPdf.classList.add('hidden');
                fileCard.classList.remove('hidden');
            } catch (err) {
                loaderPdf.classList.add('hidden');
                dropZone.classList.remove('hidden');
                alert(err.message);
            }
        }
    </script>
</body>
</html>
    """

@app.post("/api/v1/sanitize")
async def sanitize_endpoint(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Format PDF requis.")

    temp_input = os.path.join(STORAGE_DIR, f"raw_{file.filename}")
    output_name = f"sanitized_{file.filename}"
    temp_output = os.path.join(STORAGE_DIR, output_name)

    try:
        with open(temp_input, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        RobustAnonymizationEngine.process_pdf(temp_input, temp_output)

        return JSONResponse({
            "status": "ok",
            "filename": output_name,
            "download_url": f"/api/v1/download/{output_name}"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/download/{filename}")
def download_endpoint(filename: str):
    path = os.path.join(STORAGE_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Fichier introuvable.")
    return FileResponse(path, media_type="application/pdf", filename=filename)

@app.delete("/api/v1/delete/{filename}")
def delete_endpoint(filename: str):
    processed_path = os.path.join(STORAGE_DIR, filename)
    raw_path = os.path.join(STORAGE_DIR, f"raw_{filename.replace('sanitized_', '')}")

    for p in [processed_path, raw_path]:
        if os.path.exists(p):
            try:
                os.remove(p)
            except OSError:
                pass

    return JSONResponse({"status": "deleted"})

@app.post("/api/v1/sanitize-text")
def sanitize_text_endpoint(req: TextAnonymizeRequest):
    res = RobustAnonymizationEngine.process_raw_text(req.text)
    return JSONResponse(res)

@app.post("/api/v1/rehydrate-text")
def rehydrate_text_endpoint(req: TextRehydrateRequest):
    restored = RobustAnonymizationEngine.rehydrate_text(req.sanitized_text, req.encrypted_vault)
    return JSONResponse({"restored_text": restored})

@app.post("/api/v1/translate-text")
def translate_text_endpoint(req: TextTranslateRequest):
    translated = RobustAnonymizationEngine.translate_locally(req.text)
    return JSONResponse({"translated_text": translated})