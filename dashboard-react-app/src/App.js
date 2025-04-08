import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home/home";
import AccountPage from "./pages/Account/AccountPage";
import LoginPage from "./pages/Login/login";
import SignUpPage from "./pages/SignUp/signup";
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
              <Route path="account" element={<AccountPage />} />
              <Route path="login" element={<LoginPage />} />
              <Route path="signup" element={<SignUpPage />} />
              <Route path="personalized" element={<Personalized />} />
              <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
    );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
