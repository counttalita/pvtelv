// For Wallet Details
export interface WalletDetails {
  id: number;
  user_id: number;
  balance: string; // Comes as string from backend
  created_at: string;
  updated_at: string;
}

// For KYC Status (matches backend KYCSubmission.to_dict() and the 'not_started' case)
export type KYCStatusVal = "not_started" | "pending_manual" | "approved" | "rejected";

export interface KYCStatusData {
  id?: number;
  user_id?: number;
  status: KYCStatusVal;
  submitted_at?: string;
  reviewed_at?: string;
  result?: string;
  documents?: any; // Keep as any for now or define further if structure is fixed
  notes?: string;
  message?: string; // For 'No KYC submission found.' case
}

// For Transaction History
export interface TransactionItem {
  id: number;
  wallet_id: number;
  type: 'deposit' | 'withdrawal' | 'fee' | string; // Allow other types
  amount: string; // Comes as string from backend
  currency: string;
  status: string;
  timestamp: string; // ISO date string
  description?: string;
  external_transaction_id?: string;
}

export interface PaginatedTransactions {
  transactions: TransactionItem[];
  page: number;
  per_page: number;
  total_pages: number;
  total_items: number;
}
