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
    {
      letter: "1",
      name: "Apple",
      job: "Software Engineer",
      location: "Austin, TX",
      description:
        "In this role you will be responsible for defining and developing ML Platform and frameworks for generative AI powered applications at Apple Product Operations.",
    },
    {
      letter: "2",
      name: "Stripe",
      job: "Data Software Engineer",
      location: "Austin, TX",
      description:
        "You’ll help build and maintain fundamental building blocks for operational and support data insights. Many parts of the company leverage and build on top of our work to improve Stripe’s support offerings, including engineering, product, operations, data science, and more. Stripe provides many products with limitless usage patterns, creating a high degree of scale and complexity for users around the world. We’re looking for people with a strong background in data engineering and analytics to help us scale while maintaining correct and complete data. ",
    },
    {
      letter: "3",
      name: "Google",
      job: "Software Engineer",
      location: "Austin, TX",
      description:
        "As a software engineer, you will work on a specific project critical to Google’s needs with opportunities to switch teams and projects as you and our fast-paced business grow and evolve. We need our engineers to be versatile, display leadership qualities and be enthusiastic to take on new problems across the full-stack as we continue to push technology forward.",
    },
    {
      letter: "4",
      name: "Uber",
      job: "Product Manager",
      location: "Austin, TX",
      description:
        "As a Product Manager on the Risk Team, you will be working on a mission-critical area focusing on making sure that our Earner fraud management is as effective and efficient as possible by building a unified product strategy and suite of products that is used by many globally, across functions, to mitigate earner fraud, in and out, at Uber.",
    },
    {
      letter: "5",
      name: "CrowdStrike",
      job: "Data Analyst",
      location: "Austin, TX",
      description:
        "This role involves sourcing data, identifying performance trends, collaborating with teams to standardize outcomes, and presenting actionable insights to improve sales enablement initiatives.",
    },
    {
      letter: "6",
      name: "Samsung",
      job: " AI Research Engineer",
      location: "Austin, TX",
      description:
        "Conduct cutting-edge research and development of large foundation models (LLM, VLM, and Reasoning) for future, including model design, efficient model training, instruction tuning, prompt engineering, planning, action and related topics.",
    },
    {
      letter: "7",
      name: "Meta",
      job: "Software Engineer",
      location: "Austin, TX",
      description:
        "Helps onboard new team members, provides mentorship and enables successful ramp up on your team's code bases.",
    },
    {
      letter: "8",
      name: "Netflix",
      job: "Product Manager",
      location: "Austin, TX",
      description:
        "Your focus will be on the end-to-end experience for our users who need to leverage our AI platform to accomplish their work.",
    },
    {
      letter: "9",
      name: "Amazon",
      job: "Software Development Engineer",
      location: "Austin, TX",
      description:
        "Collaborate with experienced cross-disciplinary Amazonians to conceive, design, and bring innovative products and services to market.",
    },
    {
      letter: "10",
      name: "Bloomberg",
      job: "Financial Accounting Analyst",
      location: "Austin, TX",
      description:
        "You will perform analysis of accounting developments related to changes in U.S. GAAP, IFRS, SEC regulation, and auditing standards from the PCAOB and AICPA that will be incorporated into our financial accounting research platform.",
    },
  ];

  const comp = [
    { letter: "1", name: "Python" },
    { letter: "2", name: "Java" },
    { letter: "3", name: "Machine Learning" },
    { letter: "4", name: "Data Analytics" },
    { letter: "5", name: "C++" },
    { letter: "6", name: "JavaScript" },
    { letter: "7", name: "Git" },
    { letter: "8", name: "Research" },
    { letter: "9", name: "UI design" },
    { letter: "10", name: "HTML/CSS" },
  ];

  return (
    <div className="container">
      <h1 className="title">Your Personalized Job Trends</h1>
      <p className="para">Skill and role recommendations for you</p>
      <h1 className="title2">Based on Your Skills ...</h1>
      <p className="para2">Popular skills you may want to learn</p>
      <div className="list-bar">
        <ul className="list">
          {comp.map((company, index) => (
            <li className="list-item" key={index}>
              <div className="circle">{company.letter}</div>
              <span className="text">{company.name}</span>
            </li>
          ))}
        </ul>
          <div>
            <BarChart />
        </div>
      </div>
      <h1 className="title3">Jobs For You</h1>
      <ul className="list1">
        {companies.map((company, index) => (
          <li
            className="list1-item"
            key={index}
            onClick={() => openModal(company)}
          >
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
              <p>
                <strong>Job: </strong> {selectedCompany.job}
              </p>
              <p>
                <strong>Location: </strong> {selectedCompany.location}
              </p>
              <p>
                <strong>Description: </strong>
                <br /> {selectedCompany.description}
              </p>
            </div>
            <button onClick={closeModal}>Close</button>
          </div>
        </div>
      )}

      {/* <div>
        <BarChart />
      </div> */}
    </div>
  );
};

export default Personalized;
