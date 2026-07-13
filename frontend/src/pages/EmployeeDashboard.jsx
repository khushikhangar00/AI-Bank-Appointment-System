import { useState, useEffect } from 'react';
import api from '../api';
import { Users, Clock, Check, X, RefreshCw, Calendar, Phone, Tag, User } from 'lucide-react';

export default function EmployeeDashboard() {
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);

  const fetchQueue = async () => {
    try {
      const res = await api.get('/queue');
      setQueue(res.data);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchQueue();
    const interval = setInterval(fetchQueue, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleCancel = async (id) => {
    try {
      const res = await api.post(`/cancel/${id}`);
      alert(res.data.message);
      fetchQueue();
    } catch (err) {
      alert("Error cancelling");
    }
  };

  const handleConfirm = async (id) => {
    try {
      const res = await api.post(`/confirm/${id}`);
      alert(res.data.message);
      fetchQueue();
    } catch (err) {
      alert("Error confirming");
    }
  };

  const handleReject = async (id) => {
    try {
      const res = await api.post(`/reject/${id}`);
      alert(res.data.message);
      fetchQueue();
    } catch (err) {
      alert("Error rejecting");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-slate-800">Employee Queue Dashboard</h1>
          <p className="text-slate-500 mt-1">Real-time view of all appointments and manual approval status.</p>
        </div>
        <div className="flex gap-4 items-center">
          <div className="flex items-center gap-2 bg-white border border-slate-200 px-3 py-2 rounded-lg shadow-sm">
            <Calendar className="w-4 h-4 text-slate-500" />
            <input 
              type="date" 
              className="outline-none text-sm font-medium text-slate-700 bg-transparent"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
            />
          </div>
          <button onClick={fetchQueue} className="flex gap-2 items-center bg-white border border-slate-200 px-4 py-2 rounded-lg hover:bg-slate-50 shadow-sm text-sm font-medium">
            <RefreshCw className="w-4 h-4 text-indigo-600" />
            Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="p-5 border-b border-slate-100 bg-slate-50">
            <h2 className="font-bold flex gap-2 items-center text-slate-700">
              <Users className="w-5 h-5 text-indigo-600" />
              Live Queue Status
            </h2>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-100 text-sm font-medium text-slate-500">
                  <th className="p-4">Customer Details</th>
                  <th className="p-4">Service & Priority</th>
                  <th className="p-4">Time Slot</th>
                  <th className="p-4">Status</th>
                  <th className="p-4">Queue Pos</th>
                  <th className="p-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {queue.filter(q => q.date === selectedDate).map(item => (
                  <tr key={item.id} className="border-b border-slate-50 hover:bg-slate-50/50 transition-colors">
                    <td className="p-4">
                      <div className="flex flex-col">
                        <span className="font-bold text-slate-700">{item.name}</span>
                        <span className="text-xs text-slate-500 flex items-center gap-1 mt-1"><User className="w-3 h-3"/> ID: {item.customer_id}</span>
                        <span className="text-xs text-slate-500 flex items-center gap-1 mt-0.5"><Phone className="w-3 h-3"/> {item.mobile}</span>
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex flex-col">
                        <span className="font-medium text-slate-700">{item.purpose}</span>
                        <span className="text-xs text-slate-500 flex items-center gap-1 mt-1">
                          <Tag className="w-3 h-3"/> {item.priority}
                        </span>
                      </div>
                    </td>
                    <td className="p-4 text-slate-600 font-medium">{item.time}</td>
                    <td className="p-4">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-bold inline-flex items-center gap-1
                        ${item.status === 'Accepted' ? 'bg-emerald-100 text-emerald-700' : 
                          item.status === 'Rejected' ? 'bg-rose-100 text-rose-700' : 
                          item.status === 'Cancelled' ? 'bg-slate-100 text-slate-700' : 
                          item.status === 'Pending' ? 'bg-blue-100 text-blue-700' :
                          'bg-amber-100 text-amber-700'}`}>
                        {item.status}
                      </span>
                    </td>
                    <td className="p-4">
                      {item.queue_pos > 0 ? (
                        <div className="flex flex-col">
                          <span className="font-bold text-slate-800">#{item.queue_pos}</span>
                          <span className="text-xs text-slate-500">{item.wait}m wait</span>
                        </div>
                      ) : '-'}
                    </td>
                    <td className="p-4">
                      <div className="flex gap-2">
                        {item.status === 'Pending' && (
                          <>
                            <button onClick={() => handleConfirm(item.id)} className="text-emerald-600 hover:text-emerald-800 p-2 hover:bg-emerald-50 rounded-lg transition-colors" title="Confirm">
                              <Check className="w-4 h-4" />
                            </button>
                            <button onClick={() => handleReject(item.id)} className="text-rose-600 hover:text-rose-800 p-2 hover:bg-rose-50 rounded-lg transition-colors" title="Reject">
                              <X className="w-4 h-4" />
                            </button>
                          </>
                        )}
                        {item.status === 'Accepted' && (
                          <button onClick={() => handleCancel(item.id)} className="text-rose-600 hover:text-rose-800 p-2 hover:bg-rose-50 rounded-lg transition-colors" title="Cancel">
                            <X className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
                {queue.filter(q => q.date === selectedDate).length === 0 && !loading && (
                  <tr>
                    <td colSpan="5" className="p-8 text-center text-slate-500">No appointments for today yet.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-gradient-to-br from-indigo-600 to-blue-600 rounded-xl shadow-lg p-6 text-white">
            <h3 className="font-bold text-xl mb-1">Total Queue Load</h3>
            <p className="text-indigo-100 text-sm mb-6">Overview of all appointments</p>
            
            <div className="flex items-end justify-between">
              <div>
                <span className="text-4xl font-black">{queue.filter(q => q.date === selectedDate && q.status === 'Accepted').length}</span>
                <span className="text-indigo-200 ml-2 font-medium">Accepted</span>
              </div>
              <div className="text-right">
                <span className="text-2xl font-bold text-amber-300">{queue.filter(q => q.date === selectedDate && q.status === 'Pending').length}</span>
                <span className="text-indigo-200 block text-xs">Pending Approval</span>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <h3 className="font-bold text-slate-800 mb-4 flex gap-2 items-center">
              <Clock className="w-5 h-5 text-indigo-500" />
              FCFS Logic Active
            </h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              If a customer cancels their appointment, the AI will automatically re-assign that slot to the very next person in the waiting list who requested the same slot, maintaining strict First-Come-First-Serve order.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
