def extract_skills_from_text(text, common_skills=COMMON_TECH_SKILLS):
    """Enhanced skill extraction with better NLP capabilities."""
    if not text or not isinstance(text, str):
        print("WARNING: Empty or non-string input to extract_skills_from_text")
        return []
    
    text = text.lower()
    extracted_skills = set()  # Using a set for faster lookups and to avoid duplicates
    extracted_skills_with_confidence = {}  # Store skills with confidence score
    
    # Process with spaCy for better entity recognition

    doc = nlp(text)
    
    # Define skill context indicators - words that suggest a term is a skill
    skill_indicators = [
        'experience', 'skill', 'knowledge', 'proficiency', 'familiar', 'working with',
        'expertise', 'proficient', 'competent', 'trained in', 'certified', 'background in',
        'understanding of', 'ability to use', 'ability to work with', 'hands-on', 'exposure to'
    ]
    
    # Define words to ignore as skills - generic terms
    generic_terms = [
        'software', 'programming', 'language', 'framework', 'library', 'platform', 'tool',
        'environment', 'development', 'engineer', 'engineering', 'solution', 'system', 'quality',
        'knowledge', 'experience', 'proficiency', 'familiar', 'ability', 'skill', 'expertise',
        'proficient', 'competent', 'trained', 'certified', 'background', 'understanding', 
        'hands-on', 'exposure', 'working', 'with', 'using', 'utilize', 'implementation',
        'developing', 'designing', 'building', 'creating', 'writing', 'coding', 'implementing',
        'supporting', 'maintaining', 'troubleshooting', 'debugging', 'testing', 'deploying',
        'managing', 'leading', 'directing', 'coordinating', 'organizing'
    ]
    
    # 1. Extract skills from common skills list with confidence scoring

    for skill in common_skills:
        # Check for exact matches with word boundaries
        skill_pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(skill_pattern, text, re.IGNORECASE):
            # Calculate confidence score based on context and frequency
            confidence = 0
            matches = list(re.finditer(skill_pattern, text, re.IGNORECASE))
            
            # More mentions = higher confidence (capped at 3)
            confidence += min(len(matches), 3)
            
            # Check context around each mention
            has_skill_context = False
            for match in matches:
                start, end = match.span()
                # Get context (up to 75 chars before and after)
                context_start = max(0, start - 75)
                context_end = min(len(text), end + 75)
                context = text[context_start:context_end]
                
                # Check if it's used in a skill context
                if any(indicator in context for indicator in skill_indicators):
                    has_skill_context = True
                    confidence += 2
                    break
            
            # Store the skill with its confidence score
            if skill not in extracted_skills_with_confidence or confidence > extracted_skills_with_confidence[skill]:
                extracted_skills_with_confidence[skill] = confidence
                extracted_skills.add(skill)
    
    # 2. Extract technical entities and products (using spaCy)
    
    for ent in doc.ents:
        if ent.label_ in ["PRODUCT", "ORG"] and len(ent.text) > 2:
            candidate = ent.text.lower()
            
            # Filter out common non-skill entities and check it's not just a generic term
            if (candidate not in ["company", "organization", "team", "staff", "employee", "employer"] and
                candidate not in extracted_skills and
                not any(generic in candidate for generic in generic_terms)):
                
                # Check if it's a technology name
                confidence = 1
                context_start = max(0, ent.start_char - 75)
                context_end = min(len(text), ent.end_char + 75)
                context = text[context_start:context_end]
                
                if any(indicator in context for indicator in skill_indicators):
                    confidence += 2
                
                extracted_skills_with_confidence[candidate] = confidence
                extracted_skills.add(candidate)
    
    # 3. Look for additional technical skills beyond the common list
    # Look for specific technical patterns like X.js, X++ frameworks, etc.
    tech_patterns = [
        (r'\b[A-Za-z][\w-]*\.js\b', "JavaScript library/framework"),
        (r'\b[A-Za-z][\w-]*\+\+\b', "Programming language"),
        (r'\b[A-Za-z][\w-]*SQL\b', "Database technology"),
        (r'\b[A-Za-z][\w-]*DB\b', "Database technology"),
        (r'\b[A-Za-z][\w-]*lang\b', "Programming language")
    ]
    
    for pattern, category in tech_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            tech_name = match.group(0).lower()
            if tech_name not in extracted_skills:
                extracted_skills_with_confidence[tech_name] = 2  # Good confidence for pattern matches
                extracted_skills.add(tech_name)
    
    # 4. Extract specific technical skills from probable skill sections
    skill_section_patterns = [
        r'(?:technical skills|skills & expertise|technologies|tech stack)(?:[\s:]+)(.*?)(?:\n\n|\n\w+:|$)',
        r'(?:experience|expertise) (?:with|in)(?:[\s:]+)(.*?)(?:\.|$)',
        r'(?:proficiency|proficient) (?:with|in)(?:[\s:]+)(.*?)(?:\.|$)',
        r'(?:requirements|qualifications)(?:[\s:]*)(.*?)(?:\n\n|\n\w+:|$)'
    ]
    
    for pattern in skill_section_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
        for match in matches:
            skill_section = match.group(1).lower()
            # Look for comma or bullet separated lists in these sections
            for skill_phrase in re.split(r',|\n|•|-|;|\|', skill_section):
                skill_phrase = skill_phrase.strip()
                if 2 <= len(skill_phrase.split()) <= 3 and skill_phrase and not any(generic == skill_phrase for generic in generic_terms):
                    # Check if it contains at least one technical indicator
                    if any(tech_word in skill_phrase for tech_word in ["framework", "language", "stack", "api", "sdk", "library"]):
                        extracted_skills_with_confidence[skill_phrase] = 2
                        extracted_skills.add(skill_phrase)
    
    # 5. SPECIAL STEP: Direct check for explicitly mentioned skills
    # This step ensures we don't miss important skills due to regex issues

    critical_skills = [
    "c++", "c#", ".net", "asp.net", "node.js", "vue.js", "react.js", 
    "typescript", "javascript", "python", "java", "golang", "ruby",
    "tensorflow", "pytorch", "opencv", "docker", "kubernetes", "aws",
    "azure", "gcp", "sql", "nosql", "mongodb", "postgresql", 
    "python", "java", "javascript", "js", "typescript", "ts", "c++", "c#", "ruby", "php", "swift", 
    "kotlin", "go", "rust", "scala", "dart", "perl", "r", "matlab", "sql", "nosql", "mongodb", 
    "postgresql", "mysql", "oracle", "sql server", "cassandra", "redis", "elasticsearch", 
    "dynamodb", "firebase", "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s",
    "jenkins", "gitlab", "github", "bitbucket", "terraform", "ansible", "puppet", "chef",
    "react", "angular", "vue", "nextjs", "nodejs", "express", "django", "flask", "spring", 
    "laravel", "rails", "asp.net", "html", "css", "sass", "less", "bootstrap", "tailwind",
    "jquery", "redux", "graphql", "rest", "soap", "oauth", "jwt", "machine learning", "ml",
    "artificial intelligence", "ai", "deep learning", "dl", "natural language processing", "nlp",
    "computer vision", "cv", "data science", "big data", "hadoop", "spark", "kafka", "tableau",
    "power bi", "looker", "qlik", "excel", "vba", "linux", "unix", "windows", "macos", "ios", 
    "android", "flutter", "react native", "xamarin", "cordova", "unity", "unreal", "blender",
    "maya", "photoshop", "illustrator", "figma", "sketch", "adobe xd", "ui", "ux", "agile", 
    "scrum", "kanban", "jira", "confluence", "trello", "slack", "teams", "zoom", "git", "svn", 
    "mercurial", "cicd", "devops", "sre", "security", "penetration testing", "pen testing", 
    "ethical hacking", "cybersecurity", "blockchain", "ethereum", "solidity", "smart contracts",
    "crypto", "cryptocurrency", "nft", "web3", "serverless", "microservices", "soa", "apigateway"
    ]
    
    # Add variations of skills with special characters
    variations = {
        "c++": ["c plus plus", "cplusplus", "c-plus-plus"],
        "c#": ["c sharp", "csharp", "c-sharp"],
        "node.js": ["node js", "nodejs"],
        "vue.js": ["vue js", "vuejs"],
        "react.js": ["react js", "reactjs"]
    }
    
    for skill in critical_skills:
        # Check for the skill itself
        if skill.lower() in text.lower():
            if skill not in extracted_skills:
                extracted_skills.add(skill)
                extracted_skills_with_confidence[skill] = 3  # High confidence for explicit mentions
                            
        # Check for variations if they exist
        if skill in variations:
            for variant in variations[skill]:
                if variant.lower() in text.lower():
                    if skill not in extracted_skills:
                        extracted_skills.add(skill)
                        extracted_skills_with_confidence[skill] = 3
    
    # 6. Skill mapping and normalization
    
    cleaned_skills = []
    skill_mapping = {
        "js": "javascript",
        "ts": "typescript",
        "k8s": "kubernetes",
        "ml": "machine learning",
        "ai": "artificial intelligence",
        "dl": "deep learning",
        "nlp": "natural language processing",
        "cv": "computer vision",
        "react.js": "react",
        "reactjs": "react",
        "vue.js": "vue",
        "node.js": "nodejs",
        "golang": "go",
        "dotnet": ".net",
        "postgres": "postgresql",
        "aws cloud": "aws",
        "amazon web services": "aws",
        "microsoft azure": "azure",
        "google cloud platform": "gcp",
        "tensorflow": "tensorflow",
        "opencv": "opencv",
        "c plus plus": "c++",
        "cplusplus": "c++",
        "c-plus-plus": "c++",
        "c sharp": "c#",
        "csharp": "c#",
        "c-sharp": "c#",
        "objective c": "objective-c",
        "objective-c": "objective-c"
    }
    
    # Add plural to singular mapping
    plural_mapping = {}
    for skill in common_skills:
        if skill.endswith('s') and skill[:-1] in common_skills:
            plural_mapping[skill] = skill[:-1]
        elif not skill.endswith('s'):
            plural_mapping[f"{skill}s"] = skill
    
    skill_mapping.update(plural_mapping)
    
    # Sort skills by confidence score
    sorted_skills = sorted(
        [(skill, score) for skill, score in extracted_skills_with_confidence.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    # Keep only skills with sufficient confidence or that are in common skills list
    for skill, confidence in sorted_skills:
        if confidence >= 2 or skill in common_skills:
            # Map abbreviations and variants to standard names
            mapped_skill = skill_mapping.get(skill, skill)
            
            # Filter out skills that are just generic terms
            if mapped_skill not in generic_terms and len(mapped_skill) > 1:
                if mapped_skill not in cleaned_skills:
                    cleaned_skills.append(mapped_skill)

    return cleaned_skills