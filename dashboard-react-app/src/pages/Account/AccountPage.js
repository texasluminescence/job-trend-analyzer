import React from 'react';
import './AccountPage.css';

const AccountPage = () => {
    return (
        <section className="account-section">
                <div className="account-section-headers">
                    <h2>Account: name:</h2>
                    <h2>Personal information continued here</h2>
                </div>

                <div className="info-boxes-area">
                    <div className="info-text-box">
                        <h3>Info1</h3>
                        <p>
                        paragraph1
                        </p>
                        <button>Learn more</button>
                    </div>
                    <div className="info-text-box">
                        <h3>Info2</h3>
                        <p>
                        paragraph2
                        </p>
                        <button>Learn more</button>
                    </div>
                    <div className="info-text-box">
                        <h3>Info3</h3>
                        <p>
                        paragraph3
                        </p>
                        <button>Learn more</button>
                    </div>
                    <div className="info-text-box">
                        <h3>Info4</h3>
                        <p>
                        paragraph4
                        </p>
                        <button>Learn more</button>
                    </div>
                </div>
        </section>
    );
};

export default AccountPage