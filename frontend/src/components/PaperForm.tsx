import { useEffect, useState } from "react"
import type { FormEvent } from "react"
import { Save, X } from "lucide-react"

import type { Paper, PaperPayload } from "@/api/paper"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

type FormState = {
  title: string
  authors: string
  journal: string
  year: string
  doi: string
  abstract: string
  keywords: string
  pdf_path: string
}

type PaperFormProps = {
  editingPaper: Paper | null
  isSaving: boolean
  onCancel: () => void
  onSubmit: (payload: PaperPayload) => Promise<void>
}

const emptyForm: FormState = {
  title: "",
  authors: "",
  journal: "",
  year: "",
  doi: "",
  abstract: "",
  keywords: "",
  pdf_path: "",
}

function toPayload(form: FormState): PaperPayload {
  return {
    title: form.title.trim(),
    authors: form.authors.trim(),
    journal: form.journal.trim(),
    year: form.year ? Number(form.year) : null,
    doi: form.doi.trim() || null,
    abstract: form.abstract.trim() || null,
    keywords: form.keywords.trim(),
    pdf_path: form.pdf_path.trim() || null,
  }
}

function toFormState(paper: Paper): FormState {
  return {
    title: paper.title,
    authors: paper.authors,
    journal: paper.journal,
    year: paper.year?.toString() ?? "",
    doi: paper.doi ?? "",
    abstract: paper.abstract ?? "",
    keywords: paper.keywords,
    pdf_path: paper.pdf_path ?? "",
  }
}

function PaperForm({ editingPaper, isSaving, onCancel, onSubmit }: PaperFormProps) {
  const [form, setForm] = useState<FormState>(emptyForm)
  const [formError, setFormError] = useState<string | null>(null)

  useEffect(() => {
    setForm(editingPaper === null ? emptyForm : toFormState(editingPaper))
    setFormError(null)
  }, [editingPaper])

  function updateField(field: keyof FormState, value: string) {
    setForm((currentForm) => ({
      ...currentForm,
      [field]: value,
    }))
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setFormError(null)

    const payload = toPayload(form)
    if (!payload.title) {
      setFormError("请填写标题。")
      return
    }

    await onSubmit(payload)
    if (editingPaper === null) {
      setForm(emptyForm)
    }
  }

  return (
    <form className="space-y-5" onSubmit={handleSubmit}>
      <div className="max-h-[65vh] space-y-4 overflow-y-auto pr-1">
          {formError ? (
            <div
              className="rounded-md border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive"
              role="alert"
            >
              {formError}
            </div>
          ) : null}

          <label className="block text-sm font-medium" htmlFor="paper-title">
            标题
            <Input
              className="mt-1"
              id="paper-title"
              onChange={(event) => updateField("title", event.target.value)}
              placeholder="必填"
              required
              value={form.title}
            />
          </label>

          <label className="block text-sm font-medium" htmlFor="paper-authors">
            作者
            <Input
              className="mt-1"
              id="paper-authors"
              onChange={(event) => updateField("authors", event.target.value)}
              placeholder="多位作者可用分号分隔"
              value={form.authors}
            />
          </label>

          <div className="grid gap-3 sm:grid-cols-2">
            <label className="block text-sm font-medium" htmlFor="paper-journal">
              期刊
              <Input
                className="mt-1"
                id="paper-journal"
                onChange={(event) => updateField("journal", event.target.value)}
                value={form.journal}
              />
            </label>

            <label className="block text-sm font-medium" htmlFor="paper-year">
              年份
              <Input
                className="mt-1"
                id="paper-year"
                onChange={(event) => updateField("year", event.target.value)}
                type="number"
                value={form.year}
              />
            </label>
          </div>

          <label className="block text-sm font-medium" htmlFor="paper-doi">
            DOI
            <Input
              className="mt-1"
              id="paper-doi"
              onChange={(event) => updateField("doi", event.target.value)}
              value={form.doi}
            />
          </label>

          <label className="block text-sm font-medium" htmlFor="paper-keywords">
            关键词
            <Input
              className="mt-1"
              id="paper-keywords"
              onChange={(event) => updateField("keywords", event.target.value)}
              placeholder="多个关键词可用分号分隔"
              value={form.keywords}
            />
          </label>

          <label className="block text-sm font-medium" htmlFor="paper-abstract">
            摘要
            <textarea
              className="mt-1 min-h-24 w-full rounded-md border border-input bg-background px-3 py-2 text-sm outline-none focus-visible:ring-3 focus-visible:ring-ring/30"
              id="paper-abstract"
              onChange={(event) => updateField("abstract", event.target.value)}
              value={form.abstract}
            />
          </label>
      </div>

      <div className="flex justify-end gap-2 border-t pt-4">
        <Button disabled={isSaving} onClick={onCancel} type="button" variant="outline">
          <X />
          取消
        </Button>
        <Button disabled={isSaving} type="submit">
          <Save />
          {isSaving ? "保存中..." : editingPaper === null ? "创建论文" : "保存修改"}
        </Button>
      </div>
    </form>
  )
}

export { PaperForm }
