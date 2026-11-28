/* =========================================================
   DiagnoPC · Lógica da tela
   A tela NÃO decide nada sobre o diagnóstico: ela só guarda as
   respostas e pergunta ao motor (Python) qual é a próxima
   pergunta e qual é o resultado. (Seção 7.2 do relatório.)
   ========================================================= */

const estado = {
  fatos: {},          // fato -> true | false | null  (memória de trabalho)
  historico: [],      // [{fato, pergunta, valor, categoria}] na ordem respondida
  categoria: null,
  visitadas: new Set(),
  categorias: [],
  perguntaAtual: null,
};

const ICONES = {
  "1": '<path d="M12 3v8"/><path d="M6.3 6.3a8 8 0 1 0 11.4 0"/>',
  "2": '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/>',
  "3": '<path d="M4 15a8 8 0 1 1 16 0"/><path d="M12 15l4-5"/>',
  "4": '<path d="M10 14V5a2 2 0 1 1 4 0v9a4 4 0 1 1-4 0z"/><path d="M12 9v6"/>',
  "5": '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="12" cy="12" r="3"/><path d="M17 16h.01"/>',
  "6": '<path d="M2 9a15 15 0 0 1 20 0"/><path d="M5 12.5a10 10 0 0 1 14 0"/><path d="M8.5 16a5 5 0 0 1 7 0"/><path d="M12 19.5h.01"/>',
};

const TEXTO_VALOR = { true: "Sim", false: "Não", null: "Não sei" };
const NOME_PRIORIDADE = { alta: "Prioridade alta", media: "Prioridade média", baixa: "Prioridade baixa" };

const $ = (id) => document.getElementById(id);

async function api(rota, dados = {}) {
  const resposta = await fetch(rota, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(dados),
  });
  const json = await resposta.json();
  if (json.erro) throw new Error(json.erro);
  return json;
}

function mostrar(idTela) {
  document.querySelectorAll(".tela").forEach((t) => t.classList.remove("ativa"));
  $(idTela).classList.add("ativa");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function separarNome(nomeCompleto) {
  const i = nomeCompleto.indexOf(" (");
  if (i === -1) return { nome: nomeCompleto, desc: "" };
  return { nome: nomeCompleto.slice(0, i), desc: nomeCompleto.slice(i + 2, -1) };
}

function escapar(texto) {
  const div = document.createElement("div");
  div.textContent = texto;
  return div.innerHTML;
}

/* ---------------- Início ---------------- */
async function carregarInicio() {
  const dados = await api("/api/inicio");
  estado.categorias = dados.categorias;
  $("aviso-inicio").textContent = dados.aviso;
}

/* ---------------- Categorias ---------------- */
function telaCategorias() {
  const lista = $("lista-categorias");
  lista.innerHTML = "";
  estado.categorias.forEach((c) => {
    const { nome, desc } = separarNome(c.nome);
    const botao = document.createElement("button");
    botao.className = "cartao-categoria" + (estado.visitadas.has(c.id) ? " visitada" : "");
    botao.innerHTML = `
      <span class="icone"><svg viewBox="0 0 24 24">${ICONES[c.id] || ""}</svg></span>
      <span><strong>${escapar(nome)}</strong><span class="desc">${escapar(desc)}</span></span>`;
    botao.addEventListener("click", () => iniciarCategoria(c.id));
    lista.appendChild(botao);
  });

  const acoes = $("acoes-categorias");
  acoes.innerHTML = "";
  if (estado.historico.length) {
    const ver = document.createElement("button");
    ver.className = "btn btn-fantasma";
    ver.textContent = "Ver resultado sem investigar outra categoria";
    ver.addEventListener("click", telaResultado);
    acoes.appendChild(ver);
  }
  mostrar("tela-categorias");
}

/* ---------------- Perguntas ---------------- */
function iniciarCategoria(id) {
  estado.categoria = id;
  estado.visitadas.add(id);
  proximaPergunta();
}

async function proximaPergunta() {
  const dados = await api("/api/proxima", { categoria: estado.categoria, fatos: estado.fatos });
  if (!dados.fato) {
    telaResultado();
    return;
  }
  estado.perguntaAtual = dados;
  const nomeCategoria = estado.categorias.find((c) => c.id === estado.categoria).nome;
  $("chip-categoria").textContent = separarNome(nomeCategoria).nome;
  const daCategoria = estado.historico.filter((h) => h.categoria === estado.categoria).length;
  $("contador").textContent = `Pergunta ${daCategoria + 1}`;
  $("texto-pergunta").textContent = dados.pergunta;
  desenharHistorico();
  mostrar("tela-pergunta");
}

function responder(valor) {
  if (!estado.perguntaAtual) return;
  const { fato, pergunta } = estado.perguntaAtual;
  estado.fatos[fato] = valor;
  estado.historico.push({ fato, pergunta, valor, categoria: estado.categoria });
  estado.perguntaAtual = null;
  proximaPergunta();
}

function voltar() {
  const ultima = estado.historico[estado.historico.length - 1];
  if (!ultima || ultima.categoria !== estado.categoria) {
    // nenhuma resposta nesta categoria: volta para a escolha de categoria
    if (!estado.historico.some((h) => h.categoria === estado.categoria)) {
      estado.visitadas.delete(estado.categoria);
    }
    telaCategorias();
    return;
  }
  estado.historico.pop();
  delete estado.fatos[ultima.fato];
  proximaPergunta();
}

function desenharHistorico() {
  const itens = estado.historico.filter((h) => h.categoria === estado.categoria);
  $("historico").innerHTML = itens.map((h) => `
    <div class="item-historico"><span>${escapar(h.pergunta)}</span><b>${TEXTO_VALOR[h.valor]}</b></div>`
  ).join("");
}

/* ---------------- Resultado ---------------- */
const NOME_SAIDA_INSUFICIENTE = "Não foi possível concluir com os dados informados";

async function telaResultado() {
  const r = await api("/api/resultado", { fatos: estado.fatos });
  const principal = r.grupos.find((g) => g.principal);

  $("titulo-resultado").textContent = principal
    ? `Encaminhamento: ${principal.nome}`
    : NOME_SAIDA_INSUFICIENTE;

  $("bloco-contradicoes").innerHTML = r.avisos.length ? `
    <div class="caixa alerta"><h3>Respostas contraditórias</h3>
      <ul>${r.avisos.map((c) => `<li>${escapar(c)}</li>`).join("")}</ul>
      <p>Essas respostas passaram a valer "não sei" e não foram usadas como fatos confirmados.</p>
    </div>` : "";

  const derivados = r.derivados.length ? `
    <div class="caixa vazio"><h3>Fatos derivados pelo motor</h3><ul>
      ${r.derivados.map((d) => `<li><b>${escapar(d.fato)}</b> concluído por ${d.regra} na rodada ${d.rodada}</li>`).join("")}
    </ul></div>` : "";

  $("lista-hipoteses").innerHTML = (r.grupos.length
    ? r.grupos.map((g) => `
      <section class="grupo-saida ${g.suspensa ? "suspensa" : ""}">
        <div class="hipotese-topo">
          <span class="selo regra">${g.saida}</span>
          ${g.principal ? '<span class="selo alta">Encaminhamento principal</span>' : ""}
          ${g.suspensa ? '<span class="selo media">Suspensa pela política de prioridade</span>' : ""}
          ${g.favoravel ? '<span class="selo baixa">O próprio usuário pode fazer</span>' : ""}
        </div>
        <p class="desc-saida">${escapar(g.descricao)}</p>
        ${g.regras.map((h) => `
        <article class="hipotese ${g.principal ? "alta" : g.favoravel ? "baixa" : ""}">
          <div class="hipotese-topo"><span class="selo regra">${h.id}</span></div>
          <h3>${escapar(h.hipotese)}</h3>
          <dl>
            <div class="campo"><dt>Por quê?</dt><dd>${escapar(h.porque)}</dd></div>
            <div class="campo"><dt>O que fazer</dt><dd>${escapar(h.recomendacao)}</dd></div>
            ${h.alerta ? `<div class="campo seguranca"><dt>Segurança</dt><dd>${escapar(h.alerta)}</dd></div>` : ""}
            <div class="campo"><dt>Fonte</dt><dd>${escapar(h.fonte)}</dd></div>
          </dl>
        </article>`).join("")}
      </section>`).join("")
    : `<div class="caixa vazio"><h3>DADOS_INSUFICIENTES</h3>${escapar(r.motivo)}</div>`) + derivados;

  $("bloco-aberto").innerHTML = (r.grupos.length && r.em_aberto.length) ? `
    <div class="caixa aberto"><h3>Também ficaram em aberto (faltou informação)</h3>
      <ul>${r.em_aberto.map((a) => `<li><b>${a.regra}:</b> ${escapar(a.motivo)}</li>`).join("")}</ul>
    </div>` : "";

  $("lista-respostas").innerHTML = estado.historico.map((h) =>
    `<li>${escapar(h.pergunta)} <b>${TEXTO_VALOR[h.valor]}</b></li>`).join("");
  $("trilha").textContent = r.trilha;
  $("aviso-resultado").textContent = r.aviso;
  $("mensagem-salvo").textContent = "";
  mostrar("tela-resultado");
}

async function salvarResumo() {
  const r = await api("/api/salvar", { fatos: estado.fatos });
  $("mensagem-salvo").textContent = `✔ Resumo salvo em: ${r.caminho}`;
}

function novaConsulta() {
  estado.fatos = {};
  estado.historico = [];
  estado.categoria = null;
  estado.visitadas = new Set();
  telaCategorias();
}

/* ---------------- Eventos ---------------- */
$("btn-comecar").addEventListener("click", telaCategorias);
$("btn-marca").addEventListener("click", () => mostrar("tela-inicio"));
$("btn-voltar").addEventListener("click", voltar);
$("btn-outra").addEventListener("click", telaCategorias);
$("btn-salvar").addEventListener("click", salvarResumo);
$("btn-nova").addEventListener("click", novaConsulta);

const MAPA_VALOR = { sim: true, nao: false, naosei: null };
document.querySelectorAll(".btn-resposta").forEach((b) =>
  b.addEventListener("click", () => responder(MAPA_VALOR[b.dataset.valor])));

document.addEventListener("keydown", (e) => {
  if (!$("tela-pergunta").classList.contains("ativa")) return;
  const tecla = e.key.toLowerCase();
  if (tecla === "s") responder(true);
  else if (tecla === "n") responder(false);
  else if (tecla === "?" || tecla === "/") responder(null);
  else if (tecla === "backspace") voltar();
});

carregarInicio().catch((erro) => {
  $("aviso-inicio").textContent =
    "Não consegui falar com o motor. Abra o sistema pelo comando: python servidor_web.py (" + erro.message + ")";
});
