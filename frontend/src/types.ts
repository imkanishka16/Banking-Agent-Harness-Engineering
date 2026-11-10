export type Mode = "naive" | "harnessed";

export type EventType =
  | "user_message"
  | "tool_call"
  | "tool_result"
  | "policy_block"
  | "guard_finding"
  | "approval_requested"
  | "approval_decision"
  | "transfer_declined"
  | "budget_exceeded"
  | "agent_reply";

export interface TraceEvent {
  ts: string;
  thread_id: string;
  mode: Mode;
  type: EventType;
  data: Record<string, unknown>;
}

export interface ApprovalRequest {
  type: "transfer_approval";
  tool_call_id: string;
  amount: number;
  currency: string;
  beneficiary_id: string;
  beneficiary_name: string;
  bank_name: string;
  account_number: string;
  reference: string;
  message: string;
}

export interface ChatResponse {
  thread_id: string;
  mode: Mode;
  status: "completed" | "awaiting_approval";
  reply: string | null;
  approval: ApprovalRequest | null;
  events: TraceEvent[];
}

export interface Account {
  account_id: string;
  owner_name: string;
  balance: number;
  currency: string;
}

export interface Transaction {
  transaction_id: string;
  from_account_id: string;
  beneficiary_id: string;
  amount: number;
  currency: string;
  reference: string;
  status: "PENDING" | "COMPLETED" | "FAILED";
  created_at: string;
}

export interface BankState {
  accounts: Account[];
  transactions: Transaction[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "agent" | "system";
  content: string;
}