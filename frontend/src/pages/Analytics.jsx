import { useState, useEffect } from 'react';
import api from '../api';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RechartsTooltip, Legend } from 'recharts';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { Activity, Briefcase, TrendingUp, Target, Award, Clock } from 'lucide-react';

const COLORS = ['#4f46e5', '#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#f97316'];

export default function Analytics() {
  const [data, setData] = useState({ total: 0, accepted: 0, rejected: 0, purposes: [], accuracy: "N/A", top_facility: "N/A", rush_hours: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const res = await api.get('/analytics');
        setData(res.data);
      } catch (err) {
        console.error(err);
      }
      setLoading(false);
    };
    fetchAnalytics();
  }, []);

  const topPurposes = data.purposes.sort((a,b) => b.value - a.value).slice(0, 8);

  const statusData = [
    { name: 'Accepted', value: data.accepted },
    { name: 'Rejected', value: data.rejected },
    { name: 'Wait/Suggested', value: data.total - data.accepted - data.rejected }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-800">Bank Analytics Dashboard</h1>
        <p className="text-slate-500 mt-1">Data-driven insights from the AI routing system.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex items-center gap-4">
          <div className="bg-indigo-100 p-4 rounded-xl text-indigo-600">
            <Activity className="w-8 h-8" />
          </div>
          <div>
            <p className="text-slate-500 text-sm font-medium">Total Requests</p>
            <h3 className="text-3xl font-black text-slate-800">{data.total}</h3>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex items-center gap-4">
          <div className="bg-emerald-100 p-4 rounded-xl text-emerald-600">
            <TrendingUp className="w-8 h-8" />
          </div>
          <div>
            <p className="text-slate-500 text-sm font-medium">Accepted</p>
            <h3 className="text-3xl font-black text-slate-800">{data.accepted}</h3>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex items-center gap-4">
          <div className="bg-rose-100 p-4 rounded-xl text-rose-600">
            <Briefcase className="w-8 h-8" />
          </div>
          <div>
            <p className="text-slate-500 text-sm font-medium">Rejected</p>
            <h3 className="text-3xl font-black text-slate-800">{data.rejected}</h3>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex items-center gap-4">
          <div className="bg-amber-100 p-4 rounded-xl text-amber-600">
            <Target className="w-8 h-8" />
          </div>
          <div>
            <p className="text-slate-500 text-sm font-medium">Model Accuracy</p>
            <h3 className="text-3xl font-black text-slate-800">{data.accuracy}</h3>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex items-center gap-4">
          <div className="bg-sky-100 p-4 rounded-xl text-sky-600">
            <Award className="w-8 h-8" />
          </div>
          <div>
            <p className="text-slate-500 text-sm font-medium">Most Requested Facility</p>
            <h3 className="text-xl font-bold text-slate-800 break-words">{data.top_facility}</h3>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h3 className="font-bold text-lg mb-6 text-slate-700">Top Visit Purposes</h3>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topPurposes}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="name" tick={{fontSize: 12}} interval={0} angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <RechartsTooltip cursor={{fill: '#f8fafc'}} contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} />
                <Bar dataKey="value" fill="#4f46e5" radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h3 className="font-bold text-lg mb-6 text-slate-700">AI Decision Distribution</h3>
          <div className="h-80 w-full flex justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={statusData}
                  cx="50%"
                  cy="50%"
                  innerRadius={80}
                  outerRadius={110}
                  paddingAngle={5}
                  dataKey="value"
                >
                  <Cell fill="#10b981" />
                  <Cell fill="#ef4444" />
                  <Cell fill="#f59e0b" />
                </Pie>
                <RechartsTooltip contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} />
                <Legend verticalAlign="bottom" height={36}/>
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mt-6">
        <h3 className="font-bold text-lg mb-6 text-slate-700 flex items-center gap-2">
          <Clock className="w-5 h-5 text-indigo-500" />
          Rush Hours Distribution
        </h3>
        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.rush_hours.sort((a,b) => a.time.localeCompare(b.time))}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="time" tick={{fontSize: 12}} />
              <YAxis />
              <RechartsTooltip cursor={{fill: '#f8fafc'}} contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} />
              <Bar dataKey="count" fill="#ec4899" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
