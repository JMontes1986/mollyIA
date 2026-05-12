# Molly IA — Diseño del Sistema

**Fecha:** 2026-05-10  
**Proyecto:** Colegio Gemelli — Asistente Virtual para Padres de Familia  
**Estado:** Aprobado

---

## 1. Visión General

Molly IA es un chatbot educativo que permite a los padres de familia del Colegio Gemelli consultar información oficial del colegio de forma ágil, disponible 24/7. Usa RAG (Retrieval-Augmented Generation) sobre documentos y fuentes del colegio. No entrena un modelo — indexa información real y la recupera en tiempo real.

**Identidad:** Pug animado (logo oficial provisto por el cliente en `/molly-logo.png`), nombre "Molly IA", paleta navy/oro/esmeralda, tipografía Cormorant Garamond + Nunito.

---

## 2. Usuarios

| Rol | Acceso | Capacidades |
|-----|--------|-------------|
| Padre de familia | Login requerido | Chat con Molly, historial de conversaciones |
| Administrador del colegio | Login con rol admin | Todo lo anterior + panel de gestión de documentos y fuentes |

**Autenticación:** Clerk — Google OAuth + email/contraseña. Sin registro manual por parte del administrador técnico.

**Rol admin:** Se asigna manualmente desde el dashboard de Clerk (`publicMetadata: { role: "admin" }`). El frontend verifica este metadata en cada ruta `/admin/*`.

---

## 3. Arquitectura

```
┌─────────────────────────────────────────────────────┐
│  Frontend — Next.js 14 + TailwindCSS (Vercel)       │
│  • Landing pública                                  │
│  • Chat con Molly (auth requerida)                  │
│  • Panel Admin (rol admin)                          │
│  • Auth: Clerk (Google + email/contraseña)          │
└─────────────────────┬───────────────────────────────┘
                      │ HTTPS / REST
┌─────────────────────▼───────────────────────────────┐
│  Backend — FastAPI Python (Railway)                 │
│  • POST /chat          → RAG + Groq                 │
│  • POST /ingest        → procesar documento         │
│  • GET  /documents     → listar docs indexados      │
│  • DELETE /documents/:id → eliminar doc             │
│  • POST /scrape        → disparar scraper manual    │
│  • GET  /stats         → métricas admin             │
│  • PostgreSQL (Railway) → usuarios, historial chats │
│  • ChromaDB (Railway)  → vectores de documentos     │
└──────┬───────────────┬────────────────┬─────────────┘
       │               │                │
   Groq API      Cloudflare R2     Scrapers
  (Llama 3.3)   (PDFs originales)  (web+social)
```

---

## 4. Fuentes de Datos

| Fuente | Método | Frecuencia |
|--------|--------|------------|
| PDFs / DOCX | Subida manual por admin → R2 → ChromaDB | On-demand |
| colgemelli.edu.co | BeautifulSoup scraper | Semanal (cron Railway) |
| Facebook (público) | Requests + parsing HTML público | Semanal |
| Instagram (público) | Instaloader o scraper HTTP | Semanal |
| YouTube | YouTube Data API v3 (free tier) — títulos + descripciones | Semanal |

Todos los scrapers se ejecutan como tareas cron dentro de Railway. El admin puede disparar re-indexación manual desde el panel.

---

## 5. Pipeline RAG

1. **Ingesta:** documento → `PyMuPDF` (PDF) / `python-docx` (Word) / `BeautifulSoup` (web) → texto plano
2. **Chunking:** fragmentos de ~500 tokens con 50 tokens de overlap (`langchain.text_splitter`)
3. **Embeddings:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` — corre en Railway, sin costo externo, soporta español
4. **Almacenamiento:** vectores + metadata en ChromaDB (Railway persistent volume)
5. **Retrieval:** cosine similarity, top-5 chunks más relevantes
6. **Generación:** Groq API (`llama-3.3-70b-versatile`) con prompt en español + chunks + historial reciente

**Prompt base de Molly:**
```
Eres Molly, la asistente virtual amigable del Colegio Gemelli (Colombia).
Respondes ÚNICAMENTE con información de los documentos oficiales del colegio.
Si no tienes información suficiente, dilo con amabilidad y sugiere contactar secretaría.
Responde siempre en español, de forma clara y concisa.
```

---

## 6. Stack Tecnológico (100% gratuito)

| Capa | Tecnología | Costo |
|------|-----------|-------|
| Frontend | Next.js 14 + TailwindCSS | $0 — Vercel free |
| Auth | Clerk (Google + email) | $0 — hasta 10k usuarios |
| Backend | FastAPI (Python 3.11) | $0 — Railway free (500h/mes) |
| LLM | Groq — Llama 3.3 70B | $0 — 14,400 req/día |
| Vector DB | ChromaDB | $0 — en Railway |
| Base de datos | PostgreSQL | $0 — Railway |
| Storage PDFs | Cloudflare R2 | $0 — hasta 10 GB |
| Embeddings | sentence-transformers (local) | $0 — corre en Railway |
| Scraping web | BeautifulSoup + Requests | $0 |
| Scraping IG | Instaloader | $0 |
| YouTube info | YouTube Data API v3 | $0 — 10k req/día |
| **Total** | | **$0 / mes** |

---

## 7. Páginas del Sistema

### 7.1 Vista Padres
- `/` — Landing pública: presentación de Molly, CTA login/registro
- `/login` — Clerk hosted UI (Google + email/contraseña)
- `/chat` — Interfaz de chat principal (auth requerida)
- `/chat/:id` — Conversación específica del historial
- `/perfil` — Datos de la cuenta

### 7.2 Panel Administrador
- `/admin` — Dashboard: KPIs (docs indexados, preguntas respondidas, padres activos)
- `/admin/documentos` — Listado de docs, upload drag-and-drop, estado indexación
- `/admin/fuentes` — Estado de scrapers (web, FB, IG, YouTube), re-indexar manual
- `/admin/conversaciones` — Log de conversaciones (sin datos privados sensibles)
- `/admin/frecuentes` — Preguntas más frecuentes detectadas
- `/admin/usuarios` — Gestión de padres registrados

---

## 8. Modelo de Datos (PostgreSQL)

```sql
-- Usuarios sincronizados desde Clerk
users (id, clerk_id, email, name, role, created_at)

-- Conversaciones
conversations (id, user_id, title, created_at, updated_at)

-- Mensajes
messages (id, conversation_id, role, content, sources_json, created_at)

-- Registro de documentos indexados
documents (id, name, category, source_type, r2_key, chunks_count, status, created_at)

-- Log de scraping
scrape_jobs (id, source, status, chunks_added, error, ran_at)
```

---

## 9. Diseño Visual

- **Paleta:** Navy `#0f1e3c`, Oro `#c9922a`, Esmeralda `#1e5c40`, Crema `#faf7f0`
- **Tipografía:** Cormorant Garamond (headings) + Nunito (body)
- **Logo:** pug oficial `/molly-logo.png` — circular navy con borde oro en la app
- **Estética:** Academia Mediterránea — elegante, premium, no genérico de IA
- **Mockups aprobados:** en `.superpowers/brainstorm/` del proyecto

---

## 10. Configuraciones Externas a Preparar

| Servicio | Acción requerida |
|----------|-----------------|
| Groq | Crear cuenta en console.groq.com → obtener API key |
| Clerk | Crear app en clerk.com → configurar Google OAuth + email |
| Cloudflare R2 | Crear bucket `molly-docs` → obtener Access Key + Secret |
| Railway | Crear proyecto → 2 servicios: FastAPI + PostgreSQL |
| Vercel | Conectar repo GitHub → deploy automático |
| YouTube Data API | Google Cloud Console → habilitar API → obtener key |

---

## 11. Fuera de Alcance (v1)

- App móvil nativa (la web es responsive)
- Notificaciones push a padres
- Integración con sistema de notas o plataforma académica
- Pagos o matrículas en línea dentro de Molly
- Soporte multiidioma (solo español por ahora)
