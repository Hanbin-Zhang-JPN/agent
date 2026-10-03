"use strict";
const $ = (id) => document.getElementById(id);
const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
let config = null, documents = [], lastAnswer = null, embeddingBusy = false;
const modeNames = {bm25:"BM25 关键词", vector:"TF-IDF 词法向量", hybrid:"混合检索 RRF"};

function status(id, text, kind = "") {
  $(id).textContent = text;
  $(id).className = "status" + (kind ? " " + kind : "");
}

async function api(path, body) {
  let response;
  try {
    response = await fetch("/api/" + path, body === undefined ? {} : {
      method:"POST", headers:{"Content-Type":"application/json", "X-RAG-Token":config.token}, body:JSON.stringify(body)
    });
  } catch { throw new Error("无法连接本地服务。请确认服务正在运行；重启后请刷新网页。"); }
  let data;
  try { data = await response.json(); } catch { throw new Error("服务未返回有效数据，请检查终端并刷新页面。"); }
  if (!response.ok) throw new Error(data.error || "请求失败。");
  return data;
}

function page(name) {
  document.querySelectorAll(".page").forEach((el) => el.classList.toggle("hidden", el.id !== "page-" + name));
  document.querySelectorAll(".nav").forEach((el) => {
    el.classList.toggle("active", el.dataset.page === name);
    el.setAttribute("aria-current", el.dataset.page === name ? "page" : "false");
  });
  $("page-name").textContent = {ask:"知识问答",library:"资料库",lab:"原理实验室"}[name];
  window.scrollTo({top:0, behavior:"instant"});
}

async function refresh() {
  const [c, d] = await Promise.all([api("config"), api("documents")]);
  config = c; documents = d.documents;
  $("stat-docs").textContent = documents.length;
  $("stat-chunks").textContent = config.chunks;
  $("stat-vectors").textContent = config.semantic_chunks;
  $("doc-count").textContent = `(${documents.length})`;
  $("model-badge").textContent = config.has_key && config.model ? "模型已接入 · 默认本地" : "本地证据模式";
  $("generate").disabled = !(config.has_key && config.model);
  if ($("generate").disabled) $("generate").checked = false;
  const ready = config.has_key && config.chunks > 0 && config.semantic_chunks === config.chunks;
  $("vector-kind").querySelector('[value="semantic"]').disabled = !ready;
  if (!ready) $("vector-kind").value = "tfidf";
  $("build-embeddings").disabled = !config.has_key || !config.chunks || embeddingBusy;
  $("pdf-note").textContent = config.pdf_supported ? "单文件最多 8 MB · 扫描件需先 OCR" : "单文件最多 8 MB · PDF 需安装可选依赖";
  $("embedding-info").textContent = config.has_key ? `${config.semantic_chunks} / ${config.chunks} 个片段有当前模型向量 · ${config.embedding_model}` : "未配置 API Key。本地检索已可使用，语义向量是可选的增强。";
  $("connection-status").textContent = config.has_key ? `服务端已配置 Key；生成模型：${config.model || "尚未设置 OPENAI_MODEL"}；向量模型：${config.embedding_model}。` : "当前服务端未配置 API Key，正在使用本地模式。";
  if (!$("eval-cases").value) $("eval-cases").value = JSON.stringify(config.eval_cases, null, 2);
  const scope = $("doc-scope").value;
  $("doc-scope").innerHTML = '<option value="all">全部资料</option>' + documents.map((d) => `<option value="${esc(d.id)}">${esc(d.name)}</option>`).join("");
  if (documents.some((d) => d.id === scope)) $("doc-scope").value = scope;
  $("document-list").innerHTML = documents.length ? documents.map((d) => `
    <article class="doc-item"><div class="doc-row"><div class="doc-title"><span class="doc-icon">▤</span><b>${esc(d.name)}</b></div>${d.demo ? '<span class="badge">示例</span>' : ''}</div>
    <div class="doc-meta">${d.chars.toLocaleString()} 字符 · ${d.chunks} 个片段 · 分块 ${d.chunk_size} / 重叠 ${d.overlap}</div>
    <div class="doc-actions"><button class="text-btn" data-open-doc="${esc(d.id)}">原文与分块 ↗</button><button class="text-btn danger" data-delete="${esc(d.id)}">删除</button></div></article>`).join("") : '<div class="empty-docs">资料库还是空的。<br>导入一份笔记，或加载示例资料。</div>';
  updateMethod();
}

function updateMethod() {
  const mode = $("search-mode").value;
  $("vector-kind").disabled = mode === "bm25";
  $("method-note").textContent = {
    hybrid:"混合检索把两个排序列表通过 RRF 合并，不直接相加不同量纲的分数。",
    bm25:"BM25 根据词频、稀有程度和片段长度排序。对名称、编号和明确关键词很有效。",
    vector:$("vector-kind").value === "semantic" ? "语义向量比较意思的接近程度。高相似度不代表来源正确，也不保证资料能回答问题。" : "本地 TF-IDF 比较词语分布的余弦相似度。它是词法基线，不能当作语义理解。"
  }[mode];
}

async function loadExamples(button) {
  button.disabled = true;
  status("import-status", "正在加载虚构示例资料……", "busy");
  status("ask-status", "正在加载示例资料……", "busy");
  try {
    const data = await api("examples", {});
    await refresh();
    const count = data.documents.filter((d) => !d.duplicate).length;
    const text = `示例资料已就绪：新增 ${count} 份，其余相同内容已跳过。`;
    status("import-status", text); status("ask-status", text); status("eval-status", text);
  } catch (error) {
    for (const id of ["import-status", "ask-status", "eval-status"]) status(id, error.message, "error");
  } finally { button.disabled = false; }
}

function ingestionOptions() {
  return {chunk_size:Number($("chunk-size").value), overlap:Number($("chunk-overlap").value)};
}

async function importFiles(files) {
  if (!files.length) return;
  if ($("file-input").disabled) return;
  $("file-input").disabled = true;
  const messages = [];
  let failures = 0;
  for (const file of files) {
    status("import-status", [...messages, `正在解析并索引：${file.name}……`].join("\n"), "busy");
    try {
      if (file.size > 8_000_000) throw new Error("文件超过 8 MB。");
      const file_base64 = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(String(reader.result).split(",")[1]);
        reader.onerror = () => reject(new Error("读取文件失败。"));
        reader.readAsDataURL(file);
      });
      const result = await api("documents", {name:file.name, file_base64, ...ingestionOptions()});
      messages.push(`${file.name}：${result.duplicate ? "内容已存在，已跳过" : `导入完成，${result.chunks} 个片段`}`);
    } catch (error) { messages.push(`${file.name}：${error.message}`); failures++; }
  }
  try { await refresh(); } catch (error) { messages.push(error.message); failures++; }
  status("import-status", messages.join("\n"), failures ? "error" : "");
  $("file-input").disabled = false; $("file-input").value = "";
}

function answerMarkup(answer, sources) {
  const known = new Set(sources.map((s) => s.citation));
  return esc(answer).replace(/\[(S\d+)\]/g, (all, id) => known.has(id) ? `<button class="cite" data-cite="${id}" aria-label="查看来源 ${id}">[${id}]</button>` : all);
}

function renderAnswer(data) {
  lastAnswer = data;
  $("answer-panel").classList.remove("empty-answer");
  $("answer-panel").innerHTML = `<div class="answer-header"><h2>来自你的资料</h2><span>${data.answer_kind === "generated" ? "模型归纳 · 请核对引用" : "本地证据摘录"}</span></div>
    <p class="answer-question">本次问题：${esc(data.question)}</p>
    ${data.warnings.map((w) => `<div class="answer-warning">${esc(w)}</div>`).join("")}
    <div class="answer-text">${answerMarkup(data.answer, data.sources)}</div>
    <div class="source-heading"><span>上下文证据 · ${data.sources.length} 个片段</span><span>点击编号核对原文</span></div>
    ${data.sources.map((s) => `<details class="source-item" id="source-${s.citation}"><summary><span>${s.citation}</span>${esc(s.name)}<small>#${s.ordinal} ＋</small></summary><pre>${esc(s.text)}</pre><div class="source-actions"><span>原文字符位置 ${s.start}–${s.end}（从 0 开始）</span><button class="text-btn" data-open-doc="${esc(s.doc_id)}" data-start="${s.start}" data-end="${s.end}">查看原文 ↗</button></div></details>`).join("")}
    <div class="answer-footer"><span>${esc(data.citation_check)} · ${data.trace.total_ms} ms${data.usage.total_tokens ? ` · ${data.usage.total_tokens} tokens` : ''}</span><button class="text-btn" id="download-trace">导出本次结果 JSON ↓</button></div>`;
  $("trace-panel").classList.remove("hidden");
  renderTrace(data.trace);
}

function table(rows, type) {
  if (!rows.length) return '<p>没有正分数候选。</p>';
  return `<div class="table-scroll"><table><thead><tr><th>名次</th><th>来源 / 片段</th><th>BM25</th><th>余弦</th><th>${type === "hybrid" ? "RRF" : "排序分数"}</th></tr></thead><tbody>${rows.map((r, i) => `<tr><td class="num">${i+1}</td><td>${esc(r.name)} #${r.ordinal}</td><td class="num">${r.bm25_score}</td><td class="num">${r.vector_score}</td><td class="num">${r.score}</td></tr>`).join("")}</tbody></table></div>`;
}

function renderTrace(t) {
  const vec = t.vector_kind === "semantic" ? "模型语义向量" : "TF-IDF 词法向量";
  $("trace-content").innerHTML = `<div class="trace-step"><h3>01 / 解析问题</h3><p>在 ${t.corpus_chunks} 个片段中检索。中文使用单字与二元字组；英文使用单词。以下为去重后的查询项。</p><div>${t.query_terms.map((v) => `<span class="term">${esc(v)}</span>`).join("") || "无可用查询词"}</div></div>
    <div class="trace-step"><h3>02 / 两路召回</h3><p>BM25：k₁ = 1.5，b = 0.75。向量：${vec}。仅保留正分数候选，每路最多 max(Top K × 4, 20) 个。本地词法检索还要求至少命中一个查询二元字组或英文词，避免仅因共享单字召回；单字问题则允许单字命中。语义向量不使用此词法过滤。</p><details><summary>BM25 排序（${t.bm25.length} 个候选）</summary>${table(t.bm25.map((r) => ({...r,score:r.bm25_score})), "bm25")}</details><details><summary>${esc(vec)} 排序（${t.vector.length} 个候选）</summary>${table(t.vector.map((r) => ({...r,score:r.vector_score})), "vector")}</details></div>
    <div class="trace-step"><h3>03 / 最终 Top K · ${esc(t.mode === "vector" ? vec : modeNames[t.mode])}</h3>${table(t.results, t.mode)}<p>${t.mode === "hybrid" ? "RRF = 1/(60 + BM25 名次) + 1/(60 + 向量名次)；未进入某路候选时，该路贡献为零。" : "本次直接使用所选检索方式的排序。"} 分数不是正确率。</p></div>
    <div class="trace-step"><h3>04 / 组装上下文</h3><p>选择 ${t.context.length} 个完整片段，使用 ${t.context_chars} / ${t.budget} 个原文字符；超过 50% 的同源跨度重叠会去重。</p>${t.skipped.length ? `<p>跳过：${t.skipped.map((s) => `${esc(s.id)}（${esc(s.reason)}）`).join("、")}</p>` : ''}<details><summary>查看提供给生成步骤的证据 JSON</summary><pre class="trace-code">${esc(JSON.stringify(t.context.map((s) => ({id:s.citation,source:s.name,chunk:s.ordinal,text:s.text})), null, 2))}</pre></details></div>
    <div class="trace-step"><h3>05 / 回答与引用编号检查</h3><p>${lastAnswer.answer_kind === "generated" ? "模型已接收问题与证据，返回的引用编号已检查。程序没有自动验证每项事实是否与原文一致。" : "本次按查询字组/英文词的重合度选取原文句子，只摘录重合度达到最佳句 60% 的片段，最多 3 个来源。语义匹配却没有词语重合时展示首个来源。这是阅读辅助启发式，不是事实核验。没有调用生成模型。"}</p>${t.instructions ? `<details><summary>查看生成指令</summary><pre class="trace-code">${esc(t.instructions)}</pre></details>` : ''}<p>检索耗时 ${t.latency_ms} ms · 总耗时 ${t.total_ms} ms</p></div>`;
}

async function runAsk(event) {
  event.preventDefault();
  if ($("ask-btn").disabled) return;
  const question = $("question").value.trim();
  if (!question) { $("question").reportValidity(); return; }
  $("ask-btn").disabled = true;
  $("ask-btn").textContent = "正在查找证据……";
  status("ask-status", $("generate").checked ? "正在检索并请求模型归纳。完成后可查看全部证据与检索过程。" : "正在检索、排序并组织证据……", "busy");
  try {
    const scope = $("doc-scope").value;
    const data = await api("ask", {question, mode:$("search-mode").value, vector_kind:$("vector-kind").value,
      top_k:Number($("top-k").value), budget:Number($("budget").value), generate:$("generate").checked,
      doc_ids:scope === "all" ? null : [scope]});
    renderAnswer(data); status("ask-status", "");
  } catch (error) { status("ask-status", error.message, "error"); }
  finally { $("ask-btn").disabled = false; $("ask-btn").innerHTML = '检索并回答 <span>↗</span>'; }
}

async function openDocument(id, start, end) {
  const dialog = $("document-dialog");
  $("dialog-title").textContent = "正在读取原文……";
  $("dialog-content").textContent = "";
  if (!dialog.open) dialog.showModal();
  try {
    const d = await api("documents/" + id);
    $("dialog-title").textContent = d.name;
    let text = esc(d.text);
    if (Number.isInteger(start) && Number.isInteger(end) && start >= 0 && end <= d.text.length) {
      text = esc(d.text.slice(0, start)) + `<mark id="source-highlight">${esc(d.text.slice(start, end))}</mark>` + esc(d.text.slice(end));
    }
    const created = new Date(d.created_at).toLocaleString("zh-CN", {timeZone:"Asia/Tokyo",hour12:false});
    $("dialog-content").innerHTML = `<div class="dialog-meta">${d.text.length.toLocaleString()} 字符 · ${d.chunks.length} 个片段 · 导入时间 ${esc(created)}（日本时间）${d.demo ? ' · 虚构教学示例' : ''}</div><pre class="document-text">${text}</pre>
      <details><summary>查看全部分块（${d.chunks.length}）</summary><div class="dialog-chunks">${d.chunks.map((c) => `<article class="chunk-box"><h4>#${c.ordinal} <span>${c.start}–${c.end}</span></h4><pre>${esc(c.text)}</pre></article>`).join("")}</div></details>
      <div class="reindex-tools"><label>块大小<input id="reindex-size" type="number" min="100" max="2000" value="${d.chunk_size}"></label><label>重叠<input id="reindex-overlap" type="number" min="0" value="${d.overlap}"></label><button class="small-btn" id="reindex-btn">重新分块</button><p>重新分块会使此文档原有语义向量失效；操作后需重新构建向量。旧问答结果是当时的快照。</p><div class="status" id="reindex-status" role="status"></div></div>`;
    $("reindex-btn").addEventListener("click", async () => {
      $("reindex-btn").disabled = true;
      try {
        const result = await api(`documents/${id}/reindex`, {chunk_size:Number($("reindex-size").value),overlap:Number($("reindex-overlap").value)});
        await refresh(); await openDocument(id); status("reindex-status", result.note);
      } catch (error) { status("reindex-status", error.message, "error"); if ($("reindex-btn")) $("reindex-btn").disabled = false; }
    });
    if ($("source-highlight")) $("source-highlight").scrollIntoView({block:"center"});
  } catch (error) { $("dialog-content").textContent = error.message; }
}

async function splitPreview() {
  $("split-btn").disabled = true;
  try {
    const data = await api("split-preview", {text:$("split-text").value,chunk_size:Number($("split-size").value),overlap:Number($("split-overlap").value)});
    $("split-results").innerHTML = data.chunks.map((c,i) => {
      const overlap = i ? Math.max(0, data.chunks[i-1].end - c.start) : 0;
      return `<article class="chunk-box"><h4>CHUNK ${c.ordinal} <span>${c.start}–${c.end}</span></h4><pre>${overlap ? `<mark>${esc(c.text.slice(0,overlap))}</mark>` : ''}${esc(c.text.slice(overlap))}</pre></article>`;
    }).join("");
    status("split-status", `${data.chunks.length} 个片段 · 绿色标记表示与前一个片段重复的原文 · 字符位置从 0 开始，结束位置不包含在内`);
  } catch (error) { status("split-status", error.message, "error"); }
  finally { $("split-btn").disabled = false; }
}

function renderEvaluation(data) {
  const percent = (v) => v === null ? "—" : `${Math.round(v*100)}%`;
  $("eval-results").innerHTML = `<div class="eval-metrics">${data.reports.map((r) => `<article class="metric-card"><h3>${esc(modeNames[r.mode])}</h3><strong>${percent(r.hit_at_k)}</strong><span>Hit@${data.top_k}</span><p>MRR@${data.top_k}：${r.mrr_at_k === null ? "—" : r.mrr_at_k.toFixed(3)}</p><p>无答案题的无候选率：${percent(r.no_candidate_rate)}</p><p>${r.latency_ms} ms · ${r.positive_cases} 道有答案题 + ${r.negative_cases} 道无答案题</p></article>`).join("")}</div>
    <p class="metric-note">${esc(data.note)}<br>Hit@K：正确证据是否出现在前 K 个片段；MRR@K：首个正确证据排名的倒数均值，越早命中越高。无候选率只衡量检索有没有返回片段。评测基于当前 ${data.corpus_chunks} 个片段，固定问题集后再比较参数。</p>
    ${data.reports.map((r) => `<details class="eval-details"><summary>${esc(modeNames[r.mode])} · 逐题结果 ＋</summary><div class="table-scroll"><table><thead><tr><th>结果</th><th>问题</th><th>首个正确证据排名</th><th>召回来源</th></tr></thead><tbody>${r.rows.map((row) => `<tr><td class="${row.pass ? "pass" : "fail"}">${row.pass ? "通过" : "未通过"}</td><td>${esc(row.question)}</td><td>${row.rank ?? (row.expected_source ? "未命中" : "无答案题")}</td><td>${row.retrieved.map(esc).join("<br>") || "没有候选"}</td></tr>`).join("")}</tbody></table></div></details>`).join("")}`;
}

document.querySelectorAll(".nav").forEach((button) => button.addEventListener("click", () => page(button.dataset.page)));
$("header-import").addEventListener("click", () => page("library"));
$("connection-btn").addEventListener("click", () => $("connection-dialog").showModal());
document.querySelectorAll("[data-close]").forEach((button) => button.addEventListener("click", () => $(button.dataset.close).close()));
document.querySelectorAll(".demo-load").forEach((button) => button.addEventListener("click", () => loadExamples(button)));
document.querySelectorAll("[data-question]").forEach((button) => button.addEventListener("click", () => { $("question").value = button.dataset.question; $("question").focus(); }));
$("search-mode").addEventListener("change", updateMethod); $("vector-kind").addEventListener("change", updateMethod);
$("generate").addEventListener("change", () => { $("model-badge").textContent = $("generate").checked ? "模型归纳已开启" : "本地证据模式"; });
for (const id of ["top-k","budget"]) $(id).addEventListener("input", () => { $(id+"-value").textContent = $(id).value + (id === "budget" ? " 字符" : ""); });
$("ask-form").addEventListener("submit", runAsk);
$("question").addEventListener("keydown", (event) => { if ((event.metaKey || event.ctrlKey) && event.key === "Enter") { event.preventDefault(); $("ask-form").requestSubmit(); } });
$("file-input").addEventListener("change", () => importFiles(Array.from($("file-input").files)));
$("drop-zone").addEventListener("dragover", (event) => { event.preventDefault(); $("drop-zone").classList.add("drag"); });
$("drop-zone").addEventListener("dragleave", () => $("drop-zone").classList.remove("drag"));
$("drop-zone").addEventListener("drop", (event) => { event.preventDefault(); $("drop-zone").classList.remove("drag"); importFiles(Array.from(event.dataTransfer.files)); });
$("save-note").addEventListener("click", async () => {
  $("save-note").disabled = true; status("import-status", "正在索引笔记……", "busy");
  try {
    const result = await api("documents", {name:$("note-name").value,text:$("note-text").value,...ingestionOptions()});
    status("import-status", result.duplicate ? "相同内容已存在，已跳过。" : `导入完成：${result.chunks} 个片段。`);
    if (!result.duplicate) $("note-text").value = "";
    await refresh();
  } catch (error) { status("import-status", error.message, "error"); }
  finally { $("save-note").disabled = false; }
});
$("build-embeddings").addEventListener("click", async () => {
  if (embeddingBusy) return;
  embeddingBusy = true; $("build-embeddings").disabled = true;
  status("embedding-status", "正在向模型接口发送资料并构建向量。请等待；大批资料可能需要数分钟。", "busy");
  try {
    const data = await api("embeddings", {});
    status("embedding-status", `完成：新增 ${data.built} 个向量，总共 ${data.total} 个片段。`);
  } catch (error) { status("embedding-status", error.message + " 已完成的批次已保存，可以重试。", "error"); }
  finally { embeddingBusy = false; try { await refresh(); } catch (error) { status("embedding-status", error.message, "error"); } }
});
$("split-btn").addEventListener("click", splitPreview);
$("eval-btn").addEventListener("click", async () => {
  $("eval-btn").disabled = true; status("eval-status", "正在用同一组问题比较三种本地检索方式……", "busy");
  try {
    let cases;
    try { cases = JSON.parse($("eval-cases").value); } catch { throw new Error("评测 JSON 格式有误，请检查逗号、引号和括号。"); }
    const data = await api("evaluate", {cases,top_k:Number($("eval-k").value)});
    renderEvaluation(data); status("eval-status", `评测完成：${data.cases} 道题 × 3 种检索方式。本次未调用外部模型。`);
  } catch (error) { status("eval-status", error.message, "error"); }
  finally { $("eval-btn").disabled = false; }
});
document.addEventListener("click", async (event) => {
  const open = event.target.closest("[data-open-doc]");
  if (open) { await openDocument(open.dataset.openDoc, open.hasAttribute("data-start") ? Number(open.dataset.start) : undefined, open.hasAttribute("data-end") ? Number(open.dataset.end) : undefined); return; }
  const del = event.target.closest("[data-delete]");
  if (del) {
    const d = documents.find((doc) => doc.id === del.dataset.delete);
    if (!confirm(`从本地资料库删除“${d?.name}”及其索引？原始文件不会受影响。`)) return;
    del.disabled = true;
    try { await api(`documents/${del.dataset.delete}/delete`, {}); await refresh(); status("import-status", "已从资料库删除。旧问答结果仍保留当时的证据快照。"); }
    catch (error) { status("import-status", error.message, "error"); del.disabled = false; }
  }
  const cite = event.target.closest("[data-cite]");
  if (cite) { const source = $("source-"+cite.dataset.cite); source.open = true; source.scrollIntoView({behavior:"smooth",block:"center"}); }
  if (event.target.closest("#download-trace") && lastAnswer) {
    const url = URL.createObjectURL(new Blob([JSON.stringify(lastAnswer,null,2)],{type:"application/json"}));
    const link = document.createElement("a"); link.href = url; link.download = `rag-result-${Date.now()}.json`; link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
});

$("split-text").value = "# 为什么 RAG 要先检索？\n\n语言模型的训练知识不一定包含你的会议纪要、内部制度或最新项目说明。RAG 在回答之前，从你的资料库找回相关片段，再把问题和片段一起提供给模型。模型的任务是根据这些证据组织答案。资料里没有的事实，应该明确说不知道。\n\n## 分块有什么作用？\n\n长文档需要拆成适当大小的块。块太小，条件和结论可能分离；块太大，多个主题混在一起，检索容易带来无关内容。重叠可以保留边界附近的上下文，但也会增加存储和重复的证据。\n\n## 检索方式如何选择？\n\nBM25 适合明确关键词和编号。TF-IDF 是容易检查的词法向量基线。模型 Embedding 能帮助查找语义相近的表达。混合检索使用 RRF 融合名次，再根据上下文预算选取完整证据。\n\n## 如何知道改进有没有用？\n\n固定一组真实问题，为每个问题标记标准证据。比较不同参数下证据的命中率和排名，再单独检查生成答案是否符合原文。检索命中和答案正确是两项不同的要求。";
refresh().then(splitPreview).catch((error) => status("ask-status", error.message + " 请确认 python3 server.py 正在运行。", "error"));
