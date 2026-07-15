export type Paper = {
  id: number
  title: string
  authors: string
  journal: string
  year: number | null
  doi: string | null
  abstract: string | null
  keywords: string
  pdf_path: string | null
  created_at: string
  updated_at: string
}

export type PaperPayload = {
  title: string
  authors: string
  journal: string
  year: number | null
  doi: string | null
  abstract: string | null
  keywords: string
  pdf_path: string | null
}

const PAPERS_ENDPOINT = "/papers"

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || `请求失败，状态码 ${response.status}`)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json() as Promise<T>
}

export function listPapers(): Promise<Paper[]> {
  return request<Paper[]>(PAPERS_ENDPOINT)
}

export function getPaper(id: number): Promise<Paper> {
  return request<Paper>(`${PAPERS_ENDPOINT}/${id}`)
}

export function searchPapers(keyword: string): Promise<Paper[]> {
  const params = new URLSearchParams({ keyword })
  return request<Paper[]>(`${PAPERS_ENDPOINT}/search?${params.toString()}`)
}

export function createPaper(payload: PaperPayload): Promise<Paper> {
  return request<Paper>(PAPERS_ENDPOINT, {
    method: "POST",
    body: JSON.stringify(payload),
  })
}

export function updatePaper(id: number, payload: PaperPayload): Promise<Paper> {
  return request<Paper>(`${PAPERS_ENDPOINT}/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  })
}

export async function uploadPaperPdf(id: number, file: File): Promise<Paper> {
  const formData = new FormData()
  formData.append("file", file)

  const response = await fetch(`${PAPERS_ENDPOINT}/${id}/upload`, {
    method: "POST",
    body: formData,
  })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || `请求失败，状态码 ${response.status}`)
  }

  return response.json() as Promise<Paper>
}

export async function importPaperPdf(file: File): Promise<Paper> {
  const formData = new FormData()
  formData.append("file", file)

  const response = await fetch(`${PAPERS_ENDPOINT}/import`, {
    method: "POST",
    body: formData,
  })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || `请求失败，状态码 ${response.status}`)
  }

  return response.json() as Promise<Paper>
}

export function deletePaper(id: number): Promise<void> {
  return request<void>(`${PAPERS_ENDPOINT}/${id}`, {
    method: "DELETE",
  })
}
