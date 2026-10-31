
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";

import Dashboard from "./pages/Dashboard";
import ContractAnalysis from "./pages/ContractAnalysis";
import PropertyInvestigation from "./pages/PropertyInvestigation";

import "./styles/global.css";

function AppLayout() {
  return (
    <div className="app-layout">
      <Sidebar />

      <main className="main-content">
        <div className="page-container">
          <Topbar />

          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/contracts" element={<ContractAnalysis />} />
            <Route path="/property" element={<PropertyInvestigation />} />
            <Route path="*" element={<Dashboard />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppLayout />
    </BrowserRouter>
  );
}
