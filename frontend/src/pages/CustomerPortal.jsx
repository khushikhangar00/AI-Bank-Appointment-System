import { useState, useEffect } from 'react';
import api from '../api';
import { Calendar, Clock, CreditCard, User, Phone, CheckCircle, AlertCircle, RefreshCw, List, Plus } from 'lucide-react';

const purposes = [
  'Account Opening', 'Cash Deposit', 'Cash Withdrawal', 'Loan Inquiry', 'Loan Approval', 
  'Locker Service', 'KYC Update', 'Debit Card Issue', 'Credit Card Issue', 'Cheque Deposit', 
  'Cheque Clearance', 'Passbook Update', 'Demand Draft', 'RTGS/NEFT', 'Document Verification', 
  'Fixed Deposit', 'Gold Loan', 'Personal Loan', 'Education Loan', 'Home Loan', 'Complaint', 'Other'
];

const timeSlots = [
  '09:30-10:00', '10:00-10:30', '10:30-11:00', '11:00-11:30', '11:30-12:00', '12:00-12:30', '12:30-13:00', 
  '14:00-14:30', '14:30-15:00', '15:00-15:30', '15:30-16:00', '16:00-16:30'
];

export default function CustomerPortal() {
  const [formData, setFormData] = useState({
    customer_id: '', name: '', mobile: '', purpose: purposes[0], 
    preferred_date: new Date().toISOString().split('T')[0], 
    preferred_time: timeSlots[0], priority: 'Normal'
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  
  const [activeTab, setActiveTab] = useState('book'); // 'book' | 'status'
  const [checkCustomerId, setCheckCustomerId] = useState('');
  const [myRequests, setMyRequests] = useState([]);
  const [loadingStatus, setLoadingStatus] = useState(false);
  
  // Recommend time effect
  useEffect(() => {
    const fetchRecommendation = async () => {
      if (formData.purpose && formData.preferred_date) {
        try {
          const res = await api.post('/recommend_time', {
            purpose: formData.purpose,
            preferred_date: formData.preferred_date
          });
          if (res.data.recommended_time) {
            setFormData(prev => ({...prev, preferred_time: res.data.recommended_time}));
          }
        } catch(err) {
          console.error("Error fetching recommendation", err);
        }
      }
    };
    fetchRecommendation();
  }, [formData.purpose, formData.preferred_date]);

  const handleCheckStatus = async (e) => {
    e?.preventDefault();
    if (!checkCustomerId) return;
    setLoadingStatus(true);
    try {
      const res = await api.get(`/customer/${checkCustomerId}/requests`);
      setMyRequests(res.data);
    } catch(err) {
      console.error(err);
      alert('Error fetching status');
    }
    setLoadingStatus(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.post('/book', formData);
      setResult(res.data);
    } catch (err) {
      console.error(err);
      alert('Error booking appointment');
    }
    setLoading(false);
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="flex gap-2 mb-6">
        <button onClick={() => setActiveTab('book')} className={`flex-1 py-3 px-4 rounded-xl font-bold flex items-center justify-center gap-2 transition-colors ${activeTab === 'book' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-200' : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'}`}>
          <Plus className="w-5 h-5" />
          Book Appointment
        </button>
        <button onClick={() => setActiveTab('status')} className={`flex-1 py-3 px-4 rounded-xl font-bold flex items-center justify-center gap-2 transition-colors ${activeTab === 'status' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-200' : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'}`}>
          <List className="w-5 h-5" />
          My Requests
        </button>
      </div>

      <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-slate-100">
        
        {activeTab === 'book' ? (
        <>
          <div className="bg-gradient-to-r from-indigo-600 to-blue-500 p-8 text-white">
            <h2 className="text-3xl font-bold mb-2">Book Your Visit</h2>
            <p className="text-indigo-100">Our AI will find the perfect slot to minimize your wait time.</p>
          </div>
          
          <form onSubmit={handleSubmit} className="p-8 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Customer ID</label>
              <div className="relative">
                <User className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                <input required type="text" className="pl-10 w-full rounded-lg border-slate-200 border p-2.5 focus:ring-2 focus:ring-indigo-500 outline-none" 
                  value={formData.customer_id} onChange={e => setFormData({...formData, customer_id: e.target.value})} />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Full Name</label>
              <input required type="text" className="w-full rounded-lg border-slate-200 border p-2.5 focus:ring-2 focus:ring-indigo-500 outline-none" 
                value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Mobile</label>
              <div className="relative">
                <Phone className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                <input required type="text" className="pl-10 w-full rounded-lg border-slate-200 border p-2.5 focus:ring-2 focus:ring-indigo-500 outline-none" 
                  value={formData.mobile} onChange={e => setFormData({...formData, mobile: e.target.value})} />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Purpose of Visit</label>
              <select className="w-full rounded-lg border-slate-200 border p-2.5 focus:ring-2 focus:ring-indigo-500 outline-none bg-white"
                value={formData.purpose} onChange={e => setFormData({...formData, purpose: e.target.value})}>
                {purposes.map(p => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Preferred Date</label>
              <div className="relative">
                <Calendar className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                <input required type="date" className="pl-10 w-full rounded-lg border-slate-200 border p-2.5 focus:ring-2 focus:ring-indigo-500 outline-none" 
                  value={formData.preferred_date} onChange={e => setFormData({...formData, preferred_date: e.target.value})} />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Preferred Time <span className="text-xs text-emerald-600 font-bold ml-2">(AI Recommended)</span></label>
              <div className="relative">
                <Clock className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                <select className="pl-10 w-full rounded-lg border-emerald-300 border-2 p-2.5 focus:ring-2 focus:ring-emerald-500 outline-none bg-emerald-50 text-emerald-900 font-medium"
                  value={formData.preferred_time} onChange={e => setFormData({...formData, preferred_time: e.target.value})}>
                  {timeSlots.map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-slate-700 mb-1">Priority Status</label>
              <div className="flex gap-4">
                {['Normal', 'Senior Citizen', 'Disabled'].map(p => (
                  <label key={p} className={`flex-1 cursor-pointer rounded-lg border p-3 text-center transition-all ${formData.priority === p ? 'border-indigo-600 bg-indigo-50 text-indigo-700 font-medium' : 'border-slate-200 hover:border-indigo-300'}`}>
                    <input type="radio" name="priority" value={p} className="hidden" 
                      checked={formData.priority === p} onChange={() => setFormData({...formData, priority: p})} />
                    {p}
                  </label>
                ))}
              </div>
            </div>
          </div>

          <button type="submit" disabled={loading} 
            className="w-full bg-indigo-600 text-white rounded-lg p-4 font-bold text-lg hover:bg-indigo-700 transition-colors flex justify-center items-center gap-2 shadow-lg shadow-indigo-200">
            {loading ? <RefreshCw className="animate-spin" /> : "Request Appointment"}
          </button>
        </form>

        {result && (
          <div className="p-8 border-t border-slate-100 bg-slate-50">
            <h3 className="text-xl font-bold mb-4">Request Status</h3>
            
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-6 text-amber-800 flex gap-4 items-start">
              <RefreshCw className="w-8 h-8 flex-shrink-0 text-amber-500" />
              <div>
                <h4 className="font-bold text-lg">Request Pending Approval</h4>
                <p className="mt-1">Your requested slot <b>{formData.preferred_time}</b> on <b>{formData.preferred_date}</b> has been received and is pending bank employee approval. Please check back later.</p>
              </div>
            </div>
          </div>
        )}
        </>
        ) : (
        <>
          <div className="bg-gradient-to-r from-slate-800 to-slate-700 p-8 text-white">
            <h2 className="text-3xl font-bold mb-2">My Requests</h2>
            <p className="text-slate-300">Check the real-time status of your appointments.</p>
          </div>
          <div className="p-8">
            <form onSubmit={handleCheckStatus} className="flex gap-4 mb-8">
              <div className="relative flex-1">
                <User className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                <input required type="text" placeholder="Enter Customer ID" className="pl-10 w-full rounded-lg border-slate-200 border p-2.5 focus:ring-2 focus:ring-indigo-500 outline-none" 
                  value={checkCustomerId} onChange={e => setCheckCustomerId(e.target.value)} />
              </div>
              <button type="submit" disabled={loadingStatus} className="bg-slate-800 text-white px-6 rounded-lg font-bold hover:bg-slate-900 transition-colors flex items-center gap-2">
                {loadingStatus ? <RefreshCw className="animate-spin w-5 h-5" /> : "Check"}
              </button>
            </form>
            
            <div className="space-y-4">
              {myRequests.length === 0 && checkCustomerId && !loadingStatus && (
                <div className="text-center text-slate-500 py-8">No requests found or click Check to load.</div>
              )}
              {myRequests.map(req => (
                <div key={req.id} className="border border-slate-200 rounded-xl p-5 hover:border-slate-300 transition-colors">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h4 className="font-bold text-slate-800 text-lg">{req.purpose}</h4>
                      <p className="text-sm text-slate-500 mt-1">Requested on {req.request_timestamp}</p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-bold inline-flex items-center
                      ${req.status === 'Accepted' ? 'bg-emerald-100 text-emerald-700' : 
                        req.status === 'Rejected' ? 'bg-rose-100 text-rose-700' : 
                        req.status === 'Cancelled' ? 'bg-slate-100 text-slate-700' : 
                        'bg-blue-100 text-blue-700'}`}>
                      {req.status}
                    </span>
                  </div>
                  <div className="flex gap-4 text-sm font-medium text-slate-700 bg-slate-50 p-3 rounded-lg">
                    <div className="flex items-center gap-1.5"><Calendar className="w-4 h-4 text-indigo-500"/> {req.preferred_date}</div>
                    <div className="flex items-center gap-1.5"><Clock className="w-4 h-4 text-indigo-500"/> {req.preferred_time}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
        )}
      </div>
    </div>
  );
}
