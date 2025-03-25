import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home/home";
import Account from "./pages/Account/account";
import Personalized from "./pages/Personalized/personalized";
import NotFound from "./pages/NotFound/notfound";
import './components/TaskBar/task-bar.css';
import TaskBar from './components/TaskBar/task-bar';

export default function App() {
  return (
      <BrowserRouter>
        <TaskBar />
          <Routes>
              <Route index element={<Home />} />
              <Route path="account" element={<Account />} />
              <Route path="personalized" element={<Personalized />} />
              <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
    );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
