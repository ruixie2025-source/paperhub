import type { Paper } from "@/api/paper"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

type DeleteDialogProps = {
  paper: Paper | null
  isDeleting: boolean
  onCancel: () => void
  onConfirm: () => void
}

function DeleteDialog({ paper, isDeleting, onCancel, onConfirm }: DeleteDialogProps) {
  return (
    <Dialog onOpenChange={(open) => !open && onCancel()} open={paper !== null}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>删除论文</DialogTitle>
          <DialogDescription>
            {paper === null
              ? "这篇论文将被删除。"
              : `确定删除“${paper.title}”吗？`}
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button disabled={isDeleting} onClick={onCancel} type="button" variant="outline">
            取消
          </Button>
          <Button disabled={isDeleting} onClick={onConfirm} type="button" variant="destructive">
            {isDeleting ? "删除中..." : "删除"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export { DeleteDialog }
