import React, { useState } from "react";
import "./personalized.css"


const Personalized = () => {
  const [modalOpen, setModalOPen] = useState(false);
  const [selectedCompany, setSelectedCompany] = useState("");

  const openModal = (company) => {
    setSelectedCompany(company);
    setModalOPen(true);
  };

  const closeModal = () => {
    setModalOPen(false);
  };

  // List of test companies
  const companies = [
    {letter: "1", name: "Apple", job: "Software Engineer", location: "Austin, TX"},
    {letter: "2", name: "Stripe", job: "Data Engineer", location: "Austin, TX"},
    {letter: "3", name: "Google", job: "Software Engineer", location: "Austin, TX"},
    {letter: "4", name: "Uber", job: "Product Manager", location: "Austin, TX"},
    {letter: "5", name: "CrowdStrike", job: "Data Analyst", location: "Austin, TX"},
    {letter: "6", name: "Samsung", job: " AI Research Scientist", location: "Austin, TX"},
    {letter: "7", name: "Meta", job: "Software Engineer", location: "Austin, TX"},
    {letter: "8", name: "Netflix", job: "Product Manager", location: "Austin, TX"},
    {letter: "9", name: "Amazon", job: "Software Development Engineer", location: "Austin, TX"},
    {letter: "10", name: "Bloomberg", job: "Financial Analyst", location: "Austin, TX"}
  ];

  return (
    <div className="container">
      <h1 className="title">
        Top Companies to Work for in your Industry
      </h1>
      <p className="para">
        Explore rankings of the best companies to work for in your industry based on your preferences.
      </p>
      <ul className="list">
        {companies.map((company, index) => (
          <li className="list-item" key={index} onClick={() => openModal(company)}>
            <div className="circle">{company.letter}</div>
            <span className="text">{company.name}</span>
            <input type="checkbox"
              className="checkbox"
              onClick={(e) => e.stopPropagation()}/>
          </li>
        ))}
      </ul>  
      {modalOpen && (
        <div className="modal-overlay">
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>{selectedCompany.name}</h2>
            
            <div className="company-details">
            <p><strong>Job: </strong> {selectedCompany.job}</p>
            <p><strong>Location: </strong> {selectedCompany.location}</p>
            </div>
            <button onClick={closeModal}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Personalized;