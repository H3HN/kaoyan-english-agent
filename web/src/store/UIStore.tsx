import {
  createContext,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from 'react'

interface UIValue {
  flashcardOpen: boolean
  setFlashcardOpen: (open: boolean) => void
  draft: string
  setDraft: (text: string) => void
}

const UIContext = createContext<UIValue | null>(null)

export function UIProvider({ children }: { children: ReactNode }) {
  const [flashcardOpen, setFlashcardOpen] = useState(false)
  const [draft, setDraft] = useState('')
  const value = useMemo(
    () => ({ flashcardOpen, setFlashcardOpen, draft, setDraft }),
    [draft, flashcardOpen],
  )
  return <UIContext.Provider value={value}>{children}</UIContext.Provider>
}

export function useUI() {
  const value = useContext(UIContext)
  if (!value) throw new Error('useUI must be used within UIProvider')
  return value
}
