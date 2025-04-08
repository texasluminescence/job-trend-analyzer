import React, { useState, useEffect } from "react";
import { Bar } from "react-chartjs-2";
import "./personalized.css";
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend);

const BarChart = () => {
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const userEmail = localStorage.getItem('userEmail');

  useEffect(() => {
    const fetchSkillsDemand = async () => {
      try {
        setLoading(true);
        
        // Fetch skills demand data
        const response = await fetch(`http://localhost:8000/industry-skills-demand?email=${encodeURIComponent(userEmail)}&limit=10`);
        
        if (!response.ok) {
          throw new Error(`API request failed with status ${response.status}`);
        }
        
        let fetchedData = await response.json();
        
        // Format data for Chart.js
        const formattedData = {
          labels: fetchedData.map(item => item.skill),
          datasets: [
            {
              label: "Demand Score",
              data: fetchedData.map(item => item.demand),
              backgroundColor: "#6495ED",
            },
            {
              label: "Job Postings (hundreds)",
              data: fetchedData.map(item => (item.job_count ? item.job_count / 100 : 0)),
              backgroundColor: "#000000",
            },
          ],
        };
        
        setChartData(formattedData);
        setError(null);
      } catch (err) {
        console.error("Error fetching skills demand data:", err);
        setError(err.message);
        
        // Set fallback data if API fails
        setChartData({
          labels: [
            "Python",
            "JavaScript",
            "SQL",
            "React",
            "AWS",
            "Git",
            "Machine Learning",
            "Docker",
            "Node.js",
            "Java"
          ],
          datasets: [
            {
              label: "Demand Score",
              data: [100, 85, 75, 70, 65, 60, 55, 50, 45, 40],
              backgroundColor: "#6495ED",
            },
            {
              label: "Job Postings (hundreds)",
              data: [12.5, 10.6, 9.4, 8.8, 8.1, 7.5, 6.9, 6.3, 5.8, 5.1],
              backgroundColor: "#000000",
            },
          ],
        });
      } finally {
        setLoading(false);
      }
    };

    if (userEmail) {
      fetchSkillsDemand();
    } else {
      // Use default data if not logged in
      setChartData({
        labels: [
          "Python",
          "JavaScript",
          "SQL",
          "React",
          "AWS",
          "Git",
          "Machine Learning",
          "Docker",
          "Node.js",
          "Java"
        ],
        datasets: [
          {
            label: "Demand Score",
            data: [100, 85, 75, 70, 65, 60, 55, 50, 45, 40],
            backgroundColor: "#6495ED",
          },
          {
            label: "Job Postings (hundreds)",
            data: [12.5, 10.6, 9.4, 8.8, 8.1, 7.5, 6.9, 6.3, 5.8, 5.1],
            backgroundColor: "#000000",
          },
        ],
      });
      setLoading(false);
    }
  }, [userEmail]);

  const options = {
    indexAxis: "y",
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        beginAtZero: true,
      },
      y: {
        beginAtZero: true,
      },
    },
    plugins: {
      title: {
        display: true,
        text: 'In-Demand Skills in Your Industry',
        font: {
          size: 16
        }
      },
      subtitle: {
        display: true,
        text: 'Based on job postings in your industry',
        font: {
          size: 12
        },
        padding: {
          bottom: 10
        }
      }
    }
  };

  if (loading) {
    return (
      <div className="bar-graph">
        <div className="loading-chart">Loading chart data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bar-graph">
        <div className="error-chart">Error loading chart: {error}</div>
      </div>
    );
  }

  return (
    <div className="bar-graph">
      <Bar data={chartData} options={options}></Bar>
    </div>
  );
};

export default BarChart;
