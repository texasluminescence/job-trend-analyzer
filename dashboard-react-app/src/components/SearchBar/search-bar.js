import React, { useState } from 'react';
import './search-bar.css'

function SearchBar ({ placeholder, onSearch, showButton = true }) {
    const [query, setQuery] = useState('')

    const handleInput = (event) => {
        setQuery(event.target.value);
    };

    const handleSearch = () => {
        onSearch(query);
    };

    return (
        <div className="search-bar">
            <input
                type = "text"
                placeholder = {placeholder}
                value = {query}
                onChange = {handleInput}
            />
            {showButton && <button onClick={handleSearch}>Search</button>}
        </div>
    )
}

export default SearchBar;