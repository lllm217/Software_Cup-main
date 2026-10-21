const SESSION_KEY = 'ssvep:algorithm-session:v1'

async function request(path, body, token) {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 20000)
  try {
    const response = await fetch(`/api/accessibility/${path}`, {
      method: 'POST', signal: controller.signal,
      headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
      body: JSON.stringify(body),
    })
    const data = await response.json()
    if (!response.ok) {
      const error = new Error(typeof data.detail === 'string' ? data.detail : '问题答案无效，请检查后重试。')
      error.status = response.status
      throw error
    }
    return data
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('服务响应超时，请稍后重试，答案已保留。')
    throw error
  } finally { clearTimeout(timeout) }
}

export async function ensureSession(userId) {
  let saved
  try { saved = JSON.parse(sessionStorage.getItem(SESSION_KEY) || 'null') } catch { /* new session */ }
  if (saved?.source === userId && saved?.access_token && saved?.student_id) return saved
  const data = { ...await request('session', {}), source: userId }
  try { sessionStorage.setItem(SESSION_KEY, JSON.stringify(data)) } catch { /* current state remains usable */ }
  return data
}

export async function generateProfile(session, answers, course, scores) {
  try { return await request('profile', { answers, course, scores }, session.access_token) }
  catch (error) {
    if (error.status === 401) {
      try { sessionStorage.removeItem(SESSION_KEY) } catch { /* storage unavailable */ }
    }
    throw error
  }
}

export function enterMain(handoff) {
  const embedded = window.parent !== window
  const mainUrl = new URL(embedded ? window.parent.location.href
    : (import.meta.env.VITE_MAIN_APP_URL || 'http://127.0.0.1:3000/'))
  mainUrl.hash = `/accessibility/complete?handoff=${encodeURIComponent(handoff)}`
  if (embedded) window.parent.location.assign(mainUrl.href)
  else window.location.assign(mainUrl.href)
}
