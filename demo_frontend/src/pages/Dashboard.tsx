import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Trash2, 
  ExternalLink, 
  RefreshCw, 
  BarChart3, 
  FileText, 
  Users, 
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Clock,
  Database
} from 'lucide-react';
import { toast } from 'sonner';

interface KYCRecord {
  id: number;
  customer_name: string;
  customer_email: string;
  email_classification?: {
    category: string;
    priority: string;
    sentiment: string;
    confidence: number;
  };
  document_analysis?: {
    document_type: string;
    confidence: number;
    entities: string[];
  };
  tamper_detection?: {
    is_authentic: boolean;
    risk_level: string;
    confidence_score: number;
  };
  confidence_score: number;
  processing_timestamp: string;
  processed_by: string;
  created_date: string;
  status: string;
}

interface UserStats {
  total_records: number;
  confidence_breakdown: {
    high: number;
    medium: number;
    low: number;
  };
  category_breakdown: {
    onboarding: number;
    dispute: number;
    other: number;
  };
  last_processing?: string;
}

interface DashboardData {
  records: KYCRecord[];
  total_count: number;
  user_stats: UserStats;
}

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState<number | null>(null);
  const [selectedRecords, setSelectedRecords] = useState<number[]>([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('auth_token');
      
      if (!token) {
        toast.error('Please log in to view your KYC data');
        window.location.href = '/login';
        return;
      }

      const response = await fetch('/api/erp/kyc/dashboard', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch dashboard data');
      }

      const data = await response.json();
      setDashboardData(data);
    } catch (error) {
      console.error('Dashboard data fetch error:', error);
      toast.error('Failed to load KYC data');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteRecord = async (recordId: number) => {
    try {
      setDeleting(recordId);
      const token = localStorage.getItem('auth_token');

      const response = await fetch(`/api/erp/kyc/records/${recordId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to delete record');
      }

      const result = await response.json();
      
      if (result.success) {
        toast.success('KYC record deleted successfully');
        fetchDashboardData(); // Refresh data
      } else {
        toast.error(result.message || 'Failed to delete record');
      }
    } catch (error) {
      console.error('Delete error:', error);
      toast.error('Failed to delete KYC record');
    } finally {
      setDeleting(null);
    }
  };

  const handleBulkDelete = async () => {
    if (selectedRecords.length === 0) {
      toast.error('Please select records to delete');
      return;
    }

    try {
      const token = localStorage.getItem('auth_token');

      const response = await fetch('/api/erp/kyc/bulk-delete', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ record_ids: selectedRecords })
      });

      const result = await response.json();
      
      if (result.success) {
        toast.success(`Successfully deleted ${result.deleted_records.length} records`);
        setSelectedRecords([]);
        fetchDashboardData();
      } else {
        toast.error(result.message || 'Bulk delete failed');
      }
    } catch (error) {
      console.error('Bulk delete error:', error);
      toast.error('Failed to delete selected records');
    }
  };

  const openOdooERP = () => {
    window.open('http://3.6.198.245:8089', '_blank');
  };

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'verified':
        return <Badge className="bg-green-100 text-green-800">✅ Verified</Badge>;
      case 'pending':
        return <Badge className="bg-yellow-100 text-yellow-800">🔄 Pending</Badge>;
      case 'flagged':
        return <Badge className="bg-red-100 text-red-800">⚠️ Flagged</Badge>;
      default:
        return <Badge className="bg-gray-100 text-gray-800">{status}</Badge>;
    }
  };

  const getConfidenceBadge = (confidence: number) => {
    if (confidence >= 0.8) {
      return <Badge className="bg-green-100 text-green-800">High ({(confidence * 100).toFixed(0)}%)</Badge>;
    } else if (confidence >= 0.5) {
      return <Badge className="bg-yellow-100 text-yellow-800">Medium ({(confidence * 100).toFixed(0)}%)</Badge>;
    } else {
      return <Badge className="bg-red-100 text-red-800">Low ({(confidence * 100).toFixed(0)}%)</Badge>;
    }
  };

  const formatDate = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleString();
    } catch {
      return dateStr;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-foreground mb-2">Loading KYC Dashboard...</h1>
          <p className="text-muted-foreground">Fetching your processing data from Odoo ERP</p>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted flex items-center justify-center">
        <Alert className="max-w-md">
          <AlertTriangle className="w-4 h-4" />
          <AlertDescription>
            Failed to load KYC data. Please try refreshing the page.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-foreground">KYC Data Dashboard</h1>
            <p className="text-muted-foreground">Manage your KYC processing records stored in Odoo ERP</p>
          </div>
          <div className="flex gap-2">
            <Button onClick={fetchDashboardData} variant="outline">
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
            <Button onClick={openOdooERP} className="bg-purple-600 hover:bg-purple-700">
              <ExternalLink className="w-4 h-4 mr-2" />
              Open Odoo ERP
            </Button>
          </div>
        </div>

        {/* Statistics Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Records</CardTitle>
              <FileText className="w-4 h-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.user_stats.total_records}</div>
              <p className="text-xs text-muted-foreground">KYC processing records</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">High Confidence</CardTitle>
              <TrendingUp className="w-4 h-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{dashboardData.user_stats.confidence_breakdown.high}</div>
              <p className="text-xs text-muted-foreground">Records with high confidence</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Onboarding</CardTitle>
              <Users className="w-4 h-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">{dashboardData.user_stats.category_breakdown.onboarding}</div>
              <p className="text-xs text-muted-foreground">Onboarding requests</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">ERP Storage</CardTitle>
              <Database className="w-4 h-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">Odoo</div>
              <p className="text-xs text-muted-foreground">Real ERP integration</p>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="records" className="space-y-4">
          <TabsList>
            <TabsTrigger value="records">Processing Records</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="records" className="space-y-4">
            {/* Bulk Actions */}
            {selectedRecords.length > 0 && (
              <Alert>
                <AlertDescription className="flex items-center justify-between">
                  <span>{selectedRecords.length} records selected</span>
                  <Button onClick={handleBulkDelete} variant="destructive" size="sm">
                    <Trash2 className="w-4 h-4 mr-2" />
                    Delete Selected
                  </Button>
                </AlertDescription>
              </Alert>
            )}

            {/* Records List */}
            <div className="grid gap-4">
              {dashboardData.records.length === 0 ? (
                <Card>
                  <CardContent className="text-center py-8">
                    <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                    <h3 className="text-lg font-medium">No KYC records found</h3>
                    <p className="text-muted-foreground mb-4">Start by processing your first KYC request</p>
                    <Button onClick={() => window.location.href = '/kyc'}>
                      Process KYC Request
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                dashboardData.records.map((record) => (
                  <Card key={record.id} className="hover:shadow-md transition-shadow">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            checked={selectedRecords.includes(record.id)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedRecords([...selectedRecords, record.id]);
                              } else {
                                setSelectedRecords(selectedRecords.filter(id => id !== record.id));
                              }
                            }}
                            className="rounded"
                          />
                          <div>
                            <CardTitle className="text-lg">{record.customer_name}</CardTitle>
                            <CardDescription>{record.customer_email}</CardDescription>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          {getStatusBadge(record.status)}
                          <Button
                            onClick={() => handleDeleteRecord(record.id)}
                            disabled={deleting === record.id}
                            variant="outline"
                            size="sm"
                          >
                            {deleting === record.id ? (
                              <RefreshCw className="w-4 h-4 animate-spin" />
                            ) : (
                              <Trash2 className="w-4 h-4" />
                            )}
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {/* Email Classification */}
                        {record.email_classification && (
                          <div>
                            <h4 className="font-medium mb-2">Email Classification</h4>
                            <div className="space-y-1">
                              <div className="flex justify-between">
                                <span className="text-sm text-muted-foreground">Category:</span>
                                <Badge variant="outline">{record.email_classification.category}</Badge>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-sm text-muted-foreground">Priority:</span>
                                <Badge variant="outline">{record.email_classification.priority}</Badge>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-sm text-muted-foreground">Confidence:</span>
                                {getConfidenceBadge(record.email_classification.confidence)}
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Document Analysis */}
                        {record.document_analysis && (
                          <div>
                            <h4 className="font-medium mb-2">Document Analysis</h4>
                            <div className="space-y-1">
                              <div className="flex justify-between">
                                <span className="text-sm text-muted-foreground">Type:</span>
                                <Badge variant="outline">{record.document_analysis.document_type}</Badge>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-sm text-muted-foreground">Entities:</span>
                                <span className="text-sm">{record.document_analysis.entities.length}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-sm text-muted-foreground">Confidence:</span>
                                {getConfidenceBadge(record.document_analysis.confidence)}
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Tamper Detection */}
                        {record.tamper_detection && (
                          <div>
                            <h4 className="font-medium mb-2">Tamper Detection</h4>
                            <div className="space-y-1">
                              <div className="flex justify-between">
                                <span className="text-sm text-muted-foreground">Authentic:</span>
                                {record.tamper_detection.is_authentic ? (
                                  <CheckCircle className="w-4 h-4 text-green-600" />
                                ) : (
                                  <AlertTriangle className="w-4 h-4 text-red-600" />
                                )}
                              </div>
                              <div className="flex justify-between">
                                <span className="text-sm text-muted-foreground">Risk:</span>
                                <Badge 
                                  variant="outline" 
                                  className={
                                    record.tamper_detection.risk_level === 'Low' ? 'text-green-700' :
                                    record.tamper_detection.risk_level === 'Medium' ? 'text-yellow-700' :
                                    'text-red-700'
                                  }
                                >
                                  {record.tamper_detection.risk_level}
                                </Badge>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-sm text-muted-foreground">Confidence:</span>
                                {getConfidenceBadge(record.tamper_detection.confidence_score)}
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                      
                      <div className="mt-4 pt-4 border-t">
                        <div className="flex justify-between items-center text-sm text-muted-foreground">
                          <span>Processed: {formatDate(record.processing_timestamp)}</span>
                          <span>Record ID: {record.id}</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          <TabsContent value="analytics" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Confidence Breakdown */}
              <Card>
                <CardHeader>
                  <CardTitle>Confidence Distribution</CardTitle>
                  <CardDescription>AI processing confidence levels</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-sm">High Confidence (80%+)</span>
                      <div className="flex items-center gap-2">
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-green-600 h-2 rounded-full" 
                            style={{ width: `${(dashboardData.user_stats.confidence_breakdown.high / dashboardData.user_stats.total_records) * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium">{dashboardData.user_stats.confidence_breakdown.high}</span>
                      </div>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Medium Confidence (50-79%)</span>
                      <div className="flex items-center gap-2">
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-yellow-600 h-2 rounded-full" 
                            style={{ width: `${(dashboardData.user_stats.confidence_breakdown.medium / dashboardData.user_stats.total_records) * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium">{dashboardData.user_stats.confidence_breakdown.medium}</span>
                      </div>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Low Confidence (&lt;50%)</span>
                      <div className="flex items-center gap-2">
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-red-600 h-2 rounded-full" 
                            style={{ width: `${(dashboardData.user_stats.confidence_breakdown.low / dashboardData.user_stats.total_records) * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium">{dashboardData.user_stats.confidence_breakdown.low}</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Category Breakdown */}
              <Card>
                <CardHeader>
                  <CardTitle>Category Distribution</CardTitle>
                  <CardDescription>Email classification categories</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Onboarding</span>
                      <div className="flex items-center gap-2">
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full" 
                            style={{ width: `${(dashboardData.user_stats.category_breakdown.onboarding / dashboardData.user_stats.total_records) * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium">{dashboardData.user_stats.category_breakdown.onboarding}</span>
                      </div>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Dispute</span>
                      <div className="flex items-center gap-2">
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-red-600 h-2 rounded-full" 
                            style={{ width: `${(dashboardData.user_stats.category_breakdown.dispute / dashboardData.user_stats.total_records) * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium">{dashboardData.user_stats.category_breakdown.dispute}</span>
                      </div>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Other</span>
                      <div className="flex items-center gap-2">
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-gray-600 h-2 rounded-full" 
                            style={{ width: `${(dashboardData.user_stats.category_breakdown.other / dashboardData.user_stats.total_records) * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium">{dashboardData.user_stats.category_breakdown.other}</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Last Processing */}
            {dashboardData.user_stats.last_processing && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    Last Processing
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Your last KYC processing was on {formatDate(dashboardData.user_stats.last_processing)}
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Dashboard;