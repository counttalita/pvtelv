import { api, ApiResponse } from './api';
import { WalletDetails, KYCStatusData, PaginatedTransactions } from '../types/apiData'; // Added PaginatedTransactions

export const walletApiService = {
  getWalletDetails: async (): Promise<ApiResponse<WalletDetails>> => {
    return api.get<WalletDetails>('/wallet/details');
  },
  getKYCStatus: async (): Promise<ApiResponse<KYCStatusData>> => {
    return api.get<KYCStatusData>('/kyc/status');
  },
  getTransactions: async (page: number = 1, perPage: number = 10): Promise<ApiResponse<PaginatedTransactions>> => {
    return api.get<PaginatedTransactions>(`/wallet/transactions?page=${page}&per_page=${perPage}`);
  }
};
