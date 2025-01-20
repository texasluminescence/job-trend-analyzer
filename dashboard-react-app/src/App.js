import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
// import Navbar from "./components/Navbar/Navbar";
// import Footer from "./components/Footer/Footer";
import Home from "./pages/Home/home";
import Account from "./pages/Account/account";
import Personalized from "./pages/Personalized/personalized";
import NotFound from "./pages/NotFound/notfound";

export default function App() {
  return (
          <BrowserRouter>
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
