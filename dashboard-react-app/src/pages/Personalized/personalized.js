import React, { useState } from "react";
import BarChart from "./personalized-bar-graph";
import "./personalized.css";


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

  const comp = [
    {letter: "1", name: "Python", job: "Software Engineer", location: "Austin, TX"},
    {letter: "2", name: "Java", job: "Data Engineer", location: "Austin, TX"},
    {letter: "3", name: "Machine learning", job: "Software Engineer", location: "Austin, TX"},
    {letter: "4", name: "Data analytics", job: "Product Manager", location: "Austin, TX"},
    {letter: "5", name: "C++", job: "Data Analyst", location: "Austin, TX"},
    {letter: "6", name: "JavaScript", job: " AI Research Scientist", location: "Austin, TX"},
    {letter: "7", name: "Git", job: "Software Engineer", location: "Austin, TX"},
    {letter: "8", name: "Research", job: "Product Manager", location: "Austin, TX"},
    {letter: "9", name: "UI design", job: "Software Development Engineer", location: "Austin, TX"},
    {letter: "10", name: "HTML/CSS", job: "Financial Analyst", location: "Austin, TX"}
  ];

  return (
    <div className="container">
      <h1 className="title">
        Your Personalized Job Trends
      </h1>
      <p className="para">
        Skill and role recommendations for you
      </p>
      <h1 className="title2">
        Based on Your Skills ...
      </h1>
      <p className="para2">
        Popular skills you may want to learn
      </p>
      <ul className="list">
        {comp.map((company, index) => (
          <li className="list-item" key={index}>
            <div className="circle">{company.letter}</div>
            <span className="text">{company.name}</span>
          </li>
        ))}
      </ul>
      <ul className="list1">
        {companies.map((company, index) => (
          <li className="list1-item" key={index} onClick={() => openModal(company)}>
            <div className="circle1">{company.letter}</div>
            <span className="text1">{company.name}</span>
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

      <div>
        <BarChart/>
      </div>
    </div>
  );
};

export default Personalized;
