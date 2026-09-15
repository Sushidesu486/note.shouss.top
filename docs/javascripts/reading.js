(() => {
  const figureLinks = document.querySelectorAll(".paper-figure a:has(img)");
  if (figureLinks.length && typeof HTMLDialogElement !== "undefined") {
    const dialog = document.createElement("dialog");
    dialog.className = "figure-dialog";
    dialog.setAttribute("aria-label", "论文原图");
    const bar = document.createElement("div");
    bar.className = "figure-dialog-bar";
    const title = document.createElement("span");
    const close = document.createElement("button");
    close.type = "button";
    close.textContent = "×";
    close.title = "关闭原图";
    close.setAttribute("aria-label", "关闭原图");
    const body = document.createElement("div");
    body.className = "figure-dialog-body";
    const image = document.createElement("img");
    body.append(image);
    bar.append(title, close);
    dialog.append(bar, body);
    document.body.append(dialog);
    close.addEventListener("click", () => dialog.close());
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) {
        const rect = dialog.getBoundingClientRect();
        if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
      }
    });
    figureLinks.forEach((link) => link.addEventListener("click", (event) => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      image.src = link.href;
      image.alt = link.querySelector("img").alt;
      title.textContent = image.alt;
      dialog.showModal();
      body.scrollTop = 0;
      body.scrollLeft = 0;
    }));
  }

  document.querySelectorAll("[data-token-tool]").forEach((tool) => {
    const fields = [...tool.querySelectorAll("input, select")];
    const outputs = tool.querySelectorAll("output");
    const error = tool.querySelector(".token-error");
    function update() {
      const [frames, height, width, stride] = fields.map((field) => Number(field.value));
      if (!fields.every((field) => field.checkValidity()) || (frames - 1) % 4 || height % stride || width % stride) {
        error.textContent = "帧数需为 4k+1，高与宽需整除所选 token 步幅；数值须在输入范围内。";
        outputs.forEach((output) => { output.value = "—"; });
        return;
      }
      error.textContent = "";
      const tokens = ((frames - 1) / 4 + 1) * (height / stride) * (width / stride);
      outputs[0].value = tokens.toLocaleString("zh-CN");
      outputs[1].value = (tokens * tokens / 1e9).toLocaleString("zh-CN", { maximumFractionDigits: 3 }) + " G";
    }
    fields.forEach((field) => field.addEventListener("input", update));
    update();
  });
})();
