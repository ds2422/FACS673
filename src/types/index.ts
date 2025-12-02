export interface InputCardProps {
  index: number;
  content: string;
  onChange: (index: number, value: string) => void;
  isActive: boolean;
}

export interface InputSectionProps {
  inputContents: string[];
  onInputChange: (index: number, value: string) => void;
  activeCount: number;
}

export interface SynthesizeButtonProps {
  isLoading: boolean;
  isDisabled: boolean;
  onClick: () => void;
}

export interface SummaryOutputProps {
  summary: string | null;
  isLoading: boolean;
  activeCount: number;
  errorMessage: string | null;
}
