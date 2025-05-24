
import React, { useState } from "react"; // Added useState
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { SecurityStatus, DefaultSecurityItems } from "@/components/dashboard/SecurityStatus";
import { KYCStatus } from "@/components/kyc/KYCStatus";
import { ArrowRight, CreditCard, Activity, Bell, AlertCircle } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { walletApiService } from "@/services/walletApiService";
import { WalletDetails, KYCStatusData, KYCStatusVal, PaginatedTransactions, TransactionItem } from "@/types/apiData"; // Added Transaction types
import { ApiResponse } from "@/services/api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"; // Added Table components

const Dashboard = () => {
  const securityItems = DefaultSecurityItems();
  const [currentPage, setCurrentPage] = useState(1);
  const transactionsPerPage = 10;
  
  const handleSetupSecurityItem = (id: string) => {
    console.log("Setting up security item:", id);
    // In a real app, this would navigate to the setup page for the specific security item
  };

  // Fetch Wallet Details
  const { 
    data: walletApiResponse, 
    isLoading: isLoadingWallet, 
    isError: isErrorWallet, 
    error: errorWallet 
  } = useQuery<ApiResponse<WalletDetails>, Error>({
    queryKey: ['walletDetails'], 
    queryFn: walletApiService.getWalletDetails 
  });
  const walletDetails = walletApiResponse?.data;

  // Fetch KYC Status
  const { 
    data: kycApiResponse, 
    isLoading: isLoadingKYC, 
    isError: isErrorKYC, 
    error: errorKYC 
  } = useQuery<ApiResponse<KYCStatusData>, Error>({
    queryKey: ['kycStatus'], 
    queryFn: walletApiService.getKYCStatus
  });
  const kycData = kycApiResponse?.data;

  // Fetch Transactions
  const { 
    data: transactionsApiResponse, 
    isLoading: isLoadingTransactions, 
    isError: isErrorTransactions, 
    error: errorTransactions 
  } = useQuery<ApiResponse<PaginatedTransactions>, Error>({
    queryKey: ['transactions', currentPage, transactionsPerPage], 
    queryFn: () => walletApiService.getTransactions(currentPage, transactionsPerPage),
    keepPreviousData: true 
  });
  const paginatedTransactions = transactionsApiResponse?.data;

  const getAccountStatusText = (status?: KYCStatusVal) => {
    if (!status) return "Loading...";
    switch (status) {
      case "approved":
        return "Account Verified";
      case "pending_manual":
        return "Verification Pending";
      case "rejected":
        return "Verification Rejected";
      case "not_started":
      default:
        return "Verification Needed";
    }
  };
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back to your secure wallet dashboard.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="icon">
            <Bell className="h-4 w-4" />
          </Button>
          <Button>
            Add Funds <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </div>
      
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="transactions">Transactions</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
        </TabsList>
        
        <TabsContent value="overview" className="space-y-4">
          {/* First Row */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Total Balance
                </CardTitle>
                <CreditCard className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                {isLoadingWallet ? (
                  <Skeleton className="h-8 w-3/4 my-1" />
                ) : isErrorWallet ? (
                  <div className="flex items-center text-sm text-red-500">
                    <AlertCircle className="mr-1 h-4 w-4" /> Error: {errorWallet?.message || 'Failed to load balance'}
                  </div>
                ) : walletDetails ? (
                  <>
                    <div className="text-2xl font-bold">ZAR {parseFloat(walletDetails.balance).toFixed(2)}</div>
                    <p className="text-xs text-muted-foreground">
                      {parseFloat(walletDetails.balance) > 0 ? "Available funds" : "Add funds to start using your wallet"}
                    </p>
                  </>
                ) : null}
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Account Status
                </CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                {isLoadingKYC ? (
                  <>
                    <Skeleton className="h-6 w-1/2 my-1" />
                    <Skeleton className="h-4 w-3/4 mt-1" />
                    <Skeleton className="h-8 w-2/5 mt-2" />
                  </>
                ) : isErrorKYC ? (
                  <div className="flex items-center text-sm text-red-500">
                     <AlertCircle className="mr-1 h-4 w-4" /> Error: {errorKYC?.message || 'Failed to load KYC status'}
                  </div>
                ) : kycData ? (
                  <>
                    <div className={`text-lg font-medium ${kycData.status === 'approved' ? 'text-green-500' : 'text-amber-500'}`}>
                      {getAccountStatusText(kycData.status)}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      {kycData.status === 'approved' ? 'Your account is fully verified.' : 'Complete KYC to unlock full features.'}
                    </p>
                    {kycData.status !== 'approved' && (
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="mt-2 text-xs"
                        onClick={() => console.log("Navigate to KYC page")} // Replace with actual navigation
                      >
                        {kycData.status === 'rejected' ? 'Re-submit KYC' : 'Complete Verification'}
                      </Button>
                    )}
                  </>
                ) : null}
              </CardContent>
            </Card>
            
            {/* Add a third card for a 3-column layout */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Recent Activity
                </CardTitle>
                <Bell className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-muted-foreground text-sm py-8 text-center">
                  No recent activity to show
                </div>
              </CardContent>
            </Card>
          </div>
          
          {/* Second Row */}
          <div className="grid gap-4 md:grid-cols-2">
            {isLoadingKYC ? (
              <Skeleton className="h-40 w-full" /> // Approximate KYCStatus component height
            ) : isErrorKYC ? (
               <Card><CardHeader><CardTitle>KYC Status</CardTitle></CardHeader><CardContent><p className="text-sm text-red-500">Error loading KYC information.</p></CardContent></Card>
            ) : kycData ? (
              <KYCStatus 
                status={kycData.status} 
                submittedAt={kycData.submitted_at} 
                rejectionReason={kycData.notes || kycData.result} 
              />
            ) : (
              <KYCStatus status="not_started" /> // Default or placeholder if no data and not loading/error
            )}
            <SecurityStatus items={securityItems} onSetupItem={handleSetupSecurityItem} />
          </div>
        </TabsContent>
        
        <TabsContent value="transactions">
          <Card>
            <CardHeader>
              <CardTitle>Transaction History</CardTitle>
              <CardDescription>
                View all your wallet transactions
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoadingTransactions ? (
                <div className="space-y-2">
                  {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-10 w-full" />)}
                </div>
              ) : isErrorTransactions ? (
                <div className="flex items-center justify-center p-8 text-red-500">
                  <AlertCircle className="mr-2 h-5 w-5" /> 
                  <p>Error loading transactions: {errorTransactions?.message || "Unknown error"}</p>
                </div>
              ) : paginatedTransactions && paginatedTransactions.transactions.length > 0 ? (
                <>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Date</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>Description</TableHead>
                        <TableHead className="text-right">Amount</TableHead>
                        <TableHead>Status</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {paginatedTransactions.transactions.map((tx: TransactionItem) => (
                        <TableRow key={tx.id}>
                          <TableCell>{new Date(tx.timestamp).toLocaleDateString()}</TableCell>
                          <TableCell className="capitalize">{tx.type}</TableCell>
                          <TableCell>{tx.description || '-'}</TableCell>
                          <TableCell className="text-right">
                            {tx.type === 'deposit' || tx.type === 'withdrawal_reversal' ? '+' : '-'}
                            {parseFloat(tx.amount).toFixed(2)} {tx.currency}
                          </TableCell>
                          <TableCell className="capitalize">{tx.status}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                  <div className="flex items-center justify-between mt-4">
                    <Button 
                      variant="outline" 
                      onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))} 
                      disabled={currentPage <= 1 || isLoadingTransactions}
                    >
                      Previous
                    </Button>
                    <span className="text-sm text-muted-foreground">
                      Page {paginatedTransactions?.page || 1} of {paginatedTransactions?.total_pages || 1}
                    </span>
                    <Button 
                      variant="outline" 
                      onClick={() => setCurrentPage(prev => prev + 1)} 
                      disabled={(paginatedTransactions && currentPage >= paginatedTransactions.total_pages) || isLoadingTransactions}
                    >
                      Next
                    </Button>
                  </div>
                </>
              ) : (
                <div className="flex items-center justify-center p-8 text-muted-foreground">
                  <p>No transactions yet</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="security">
          <Card>
            <CardHeader>
              <CardTitle>Security Settings</CardTitle>
              <CardDescription>
                Manage your account security preferences
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <SecurityStatus items={securityItems} onSetupItem={handleSetupSecurityItem} />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Dashboard;
