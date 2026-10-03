(() => {
  "use strict";
  const lessons = window.CSS_LAB_LESSONS;
  const storageKey = "css-lab-progress-v1";
  const el = (id) => document.getElementById(id);
  const ui = {
    nav: el("lesson-nav"), fraction: el("progress-fraction"),
    track: el("progress-track"), fill: el("progress-fill"),
    breadcrumb: el("breadcrumb-title"), number: el("lesson-number"),
    duration: el("lesson-duration"), title: el("lesson-title"),
    subtitle: el("lesson-subtitle"), conceptTitle: el("concept-title"),
    conceptBody: el("concept-body"), conceptCode: el("concept-code"),
    taskIntro: el("task-intro"), taskList: el("task-list"),
    hintButton: el("hint-button"), hintBox: el("hint-box"),
    htmlTab: el("html-tab"), cssTab: el("css-tab"),
    htmlEditor: el("html-editor"), cssEditor: el("css-editor"),
    resetButton: el("reset-button"), preview: el("preview-frame"),
    previewStage: el("preview-stage"), desktopButton: el("desktop-button"),
    mobileButton: el("mobile-button"), previewSize: el("preview-size"),
    solutionButton: el("solution-button"), solutionPanel: el("solution-panel"),
    solutionCode: el("solution-code"), useSolutionButton: el("use-solution-button"),
    completeButton: el("complete-button"), nextButton: el("next-button")
  };

  function readSaved() {
    try {
      const value = JSON.parse(localStorage.getItem(storageKey));
      return value && typeof value === "object" ? value : {};
    } catch {
      return {};
    }
  }
  const saved = readSaved();
  const progress = saved.progress && typeof saved.progress === "object" ? saved.progress : {};
  const drafts = saved.drafts && typeof saved.drafts === "object" ? saved.drafts : {};
  let currentIndex = 0;
  let previewTimer;
  const currentLesson = () => lessons[currentIndex];

  function persist() {
    try { localStorage.setItem(storageKey, JSON.stringify({ progress, drafts })); }
    catch { /* The editor still works when storage is unavailable. */ }
  }
  function draftFor(lesson) {
    const draft = drafts[lesson.id];
    return {
      html: draft && typeof draft.html === "string" ? draft.html : lesson.html,
      css: draft && typeof draft.css === "string" ? draft.css : lesson.starter
    };
  }
  function saveDraft() {
    drafts[currentLesson().id] = { html: ui.htmlEditor.value, css: ui.cssEditor.value };
    persist();
  }
  function renderNavigation() {
    ui.nav.replaceChildren();
    let categoryName = "";
    lessons.forEach((lesson, index) => {
      if (lesson.category !== categoryName) {
        const category = document.createElement("div");
        category.className = "nav-category";
        category.textContent = lesson.category;
        ui.nav.append(category);
        categoryName = lesson.category;
      }
      const button = document.createElement("button");
      button.type = "button";
      button.className = "lesson-link";
      button.setAttribute("aria-current", index === currentIndex ? "step" : "false");
      button.innerHTML = '<span class="lesson-link-number"></span><span class="lesson-link-title"></span><span class="lesson-link-status" aria-hidden="true"></span>';
      button.querySelector(".lesson-link-number").textContent = String(index + 1).padStart(2, "0");
      button.querySelector(".lesson-link-title").textContent = lesson.title;
      button.querySelector(".lesson-link-status").textContent = progress[lesson.id] ? "✓" : "↗";
      if (index === currentIndex) button.classList.add("active");
      if (progress[lesson.id]) button.classList.add("done");
      button.addEventListener("click", () => {
        selectLesson(index);
        window.scrollTo({ top: 0, behavior: "smooth" });
      });
      ui.nav.append(button);
    });
    const done = lessons.filter((lesson) => progress[lesson.id]).length;
    ui.fraction.textContent = done + " / " + lessons.length;
    ui.track.setAttribute("aria-valuemax", String(lessons.length));
    ui.track.setAttribute("aria-valuenow", String(done));
    ui.fill.style.width = (done / lessons.length * 100) + "%";
  }
  function renderCompletion() {
    const done = Boolean(progress[currentLesson().id]);
    ui.completeButton.classList.toggle("is-complete", done);
    ui.completeButton.innerHTML = done
      ? '已完成 <span aria-hidden="true">✓</span>'
      : '标记为已完成 <span aria-hidden="true">✓</span>';
    ui.completeButton.setAttribute("aria-pressed", String(done));
  }
  function selectLesson(index) {
    currentIndex = index;
    const lesson = currentLesson();
    const draft = draftFor(lesson);
    ui.breadcrumb.textContent = lesson.title;
    ui.number.textContent = "LESSON " + String(index + 1).padStart(2, "0");
    ui.duration.textContent = "约 " + lesson.duration;
    ui.title.textContent = lesson.title;
    ui.subtitle.textContent = lesson.subtitle;
    ui.conceptTitle.textContent = lesson.conceptTitle;
    ui.conceptBody.textContent = lesson.conceptBody;
    ui.conceptCode.textContent = lesson.conceptCode;
    ui.taskIntro.textContent = lesson.taskIntro;
    ui.taskList.replaceChildren();
    lesson.tasks.forEach((task) => {
      const item = document.createElement("li");
      item.textContent = task;
      ui.taskList.append(item);
    });
    ui.hintBox.textContent = lesson.hint;
    ui.hintBox.hidden = true;
    ui.hintButton.setAttribute("aria-expanded", "false");
    ui.htmlEditor.value = draft.html;
    ui.cssEditor.value = draft.css;
    ui.solutionCode.textContent = lesson.solution;
    ui.solutionPanel.hidden = true;
    ui.solutionButton.setAttribute("aria-expanded", "false");
    ui.nextButton.innerHTML = index === lessons.length - 1
      ? '回到第一课 <span aria-hidden="true">↗</span>'
      : '下一课 <span aria-hidden="true">→</span>';
    renderNavigation();
    renderCompletion();
    updatePreview();
    history.replaceState(null, "", "#" + lesson.id);
  }
  function updatePreview() {
    const html = ui.htmlEditor.value;
    const css = ui.cssEditor.value.replace(/<\/style/gi, "<\\/style");
    const base = '*,*::before,*::after{box-sizing:border-box}html{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}body{margin:0;padding:24px;color:#292b39;background:#f7f6f2}button{font-family:inherit}';
    ui.preview.srcdoc = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><style>' + base + '</style><style>' + css + '</style></head><body>' + html + '</body></html>';
  }
  function queuePreview() {
    saveDraft();
    clearTimeout(previewTimer);
    previewTimer = setTimeout(updatePreview, 140);
  }
  function showTab(tab) {
    const htmlActive = tab === "html";
    ui.htmlEditor.hidden = !htmlActive;
    ui.cssEditor.hidden = htmlActive;
    ui.htmlTab.classList.toggle("active", htmlActive);
    ui.cssTab.classList.toggle("active", !htmlActive);
    ui.htmlTab.setAttribute("aria-selected", String(htmlActive));
    ui.cssTab.setAttribute("aria-selected", String(!htmlActive));
    ui.htmlTab.tabIndex = htmlActive ? 0 : -1;
    ui.cssTab.tabIndex = htmlActive ? -1 : 0;
  }
  function setViewport(mobile) {
    ui.previewStage.classList.toggle("mobile", mobile);
    ui.desktopButton.classList.toggle("active", !mobile);
    ui.mobileButton.classList.toggle("active", mobile);
    ui.desktopButton.setAttribute("aria-pressed", String(!mobile));
    ui.mobileButton.setAttribute("aria-pressed", String(mobile));
    ui.previewSize.textContent = mobile ? "手机视图 · 360px" : "桌面视图";
  }

  ui.htmlTab.addEventListener("click", () => showTab("html"));
  ui.cssTab.addEventListener("click", () => showTab("css"));
  ui.htmlEditor.addEventListener("input", queuePreview);
  ui.cssEditor.addEventListener("input", queuePreview);
  ui.resetButton.addEventListener("click", () => {
    const lesson = currentLesson();
    delete drafts[lesson.id];
    ui.htmlEditor.value = lesson.html;
    ui.cssEditor.value = lesson.starter;
    persist();
    updatePreview();
  });
  ui.hintButton.addEventListener("click", () => {
    ui.hintBox.hidden = !ui.hintBox.hidden;
    ui.hintButton.setAttribute("aria-expanded", String(!ui.hintBox.hidden));
  });
  ui.solutionButton.addEventListener("click", () => {
    ui.solutionPanel.hidden = !ui.solutionPanel.hidden;
    ui.solutionButton.setAttribute("aria-expanded", String(!ui.solutionPanel.hidden));
  });
  ui.useSolutionButton.addEventListener("click", () => {
    ui.cssEditor.value = currentLesson().solution;
    showTab("css");
    saveDraft();
    updatePreview();
    ui.cssEditor.focus();
  });
  ui.completeButton.addEventListener("click", () => {
    progress[currentLesson().id] = !progress[currentLesson().id];
    persist();
    renderNavigation();
    renderCompletion();
  });
  ui.nextButton.addEventListener("click", () => {
    selectLesson((currentIndex + 1) % lessons.length);
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
  ui.desktopButton.addEventListener("click", () => setViewport(false));
  ui.mobileButton.addEventListener("click", () => setViewport(true));
  document.querySelector('a[href="#workspace"]').addEventListener("click", (event) => {
    event.preventDefault();
    el("workspace").scrollIntoView({ behavior: "smooth", block: "start" });
  });
  document.addEventListener("keydown", (event) => {
    if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
      event.preventDefault();
      clearTimeout(previewTimer);
      updatePreview();
    }
  });
  window.addEventListener("hashchange", () => {
    const index = lessons.findIndex((lesson) => lesson.id === location.hash.slice(1));
    if (index >= 0 && index !== currentIndex) selectLesson(index);
  });
  const initialIndex = lessons.findIndex((lesson) => lesson.id === location.hash.slice(1));
  showTab("css");
  setViewport(false);
  selectLesson(initialIndex >= 0 ? initialIndex : 0);
})();
