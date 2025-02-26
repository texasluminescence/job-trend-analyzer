import React from 'react';
import { Bar } from 'react-chartjs-2';
import "./personalized.css"
import {
    Chart as ChartJS,
    BarElement,
    CategoryScale,
    LinearScale,
    Tooltip,



    Legend
} from 'chart.js'


ChartJS.register(
    BarElement,
    CategoryScale,
    LinearScale,
    Tooltip,
    Legend
)

const BarChart = () => {
    const data = {
        labels: ['Apple', "Stripe", "Google", "Uber", "CrowdStrike", "Samsung", "Meta", "Netflix", "Amazon", "Bloomberg"],
        datasets: [
            {
                label: 'Number of Applicants',
                data: [1710, 1452, 2098, 1607, 1420, 1453, 1910, 1112, 1998, 1245],
                backgroundColor: '#ff1493'
            },
            {
                label: 'Number of Accepted Applicants',
                data: [678, 458, 975, 231, 187, 915, 523, 389, 781, 805],
                backgroundColor: '#8a2be2'
            }
        ]
    }
    const options = {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                beginAtZero: true
            },

            y: {
                beginAtZero: true
            }
        }

    }


    return (
        <div className='bar-graph'>
            <Bar data={data} options={options}></Bar>
        </div>
    )
}

export default BarChart;