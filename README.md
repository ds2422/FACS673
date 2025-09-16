# FACS673 Team 2 - AI Summarizer

## Team Roster:

* **Dhairya Shah**: Microservices developer
* **Monil Baxi**: Frontend Developer
* **Shriya Sharma**: Frontend Developer
* **Praise Adegbite**: Database Developer
* **Shivani Reddy**: Microservices developer

## Far Vision (Long-Term Product Vision):

Our ultimate goal is to become the leading platform for knowledge synthesis, transforming how students, professionals, and researchers consume information. Over the next 5-10 years, we envision the AI Summarizer evolving from a simple summarization tool into an indispensable research assistant. This will involve integrating advanced features like personalized knowledge graphs, collaborative summary workspaces, and real-time summarization of live lectures or conference calls. Our aim is to not only condense information but to empower users to understand, compare, and act on insights from vast amounts of data, ultimately saving them countless hours and enhancing their productivity. 

## Near Vision (First Iteration Goal)

The first iteration focuses on building a functional Minimum Viable Product (MVP) that provides core value to our target users. Our primary goal is to deliver a robust, user-friendly tool that can generate accurate summaries from various text sources. In the next 2-3 years we plan to preserve the history specific to the users. Currently the user can access the history as long as the page is not refreshed or the user logs out. Along with this, the products would also support summarization for more than 2 inputs provided by the user.

**Key Features & Deliverables for MVP**:
* **Multiple-Source Summarization**: Users can submit one URL (article, blog post) along with a single document (text file, PDF) and receive a concise summary.
* **Transcript Summarization**: Users can upload a video transcript (text file) and get a summary.
* **Basic User Interface**: A clean, intuitive web interface built with TypeScript for submitting content and viewing summaries.
* **Backend Integration**: A Django backend to handle API requests and communicate with the AI model.
* **AI Model Integration**: A pre-trained Hugging Face Transformer model for summary generation.
* **Deployment**: The application will be deployed and accessible to a limited beta group via Vercel and Render.


## Stakeholders

* Students: Want to quickly grasp the main points of long articles, research papers, or lecture notes to save time while studying and preparing for exams. They need a tool to make their learning more efficient.
* Working Professionals: Seek to stay updated on industry trends, synthesize key takeaways from reports, and quickly digest meeting transcripts to make faster, more informed decisions.
* Researchers: Need to review and compare a large volume of academic papers to identify key findings, methodologies, and gaps in the literature. They require a tool to streamline their literature review process.

## Detailed User Persona

**Name: Alex Chen**
**Background:**
Alex, a 21-year-old computer science student at a major university, juggles multiple courses, a part-time internship, and a capstone project. He spends hours reading technical documentation, research papers, and online articles to stay updated on technology.

**Motivations:**
* Efficiency: He wants to minimize the time spent on repetitive tasks like reading long articles.
* Academic Success: He needs to get good grades and finish his capstone project on time.
* Skill Development: He’s motivated to learn and retain information from technical papers quickly.

**Frustration:**
* Information Overload: Feels overwhelmed by the sheer volume of reading required for his classes.
* Time Constraints: Not enough time in the day to read every article or paper in its entirety.
* Difficulty Identifying Key Points: Often struggles to find the most critical information in dense, academic texts.

**Goals:**
* To quickly prepare for exams by summarizing lecture notes and readings.
* To rapidly synthesize information for his capstone project literature review.
* To stay on top of new developments in his field without sacrificing sleep.

---

##  Initial Product Backlog
📍 Instead of Pivot Tracker we did it using Jira: 
[Jira Link](https://njit-team-fhi2acbj.atlassian.net/jira/software/projects/CT/boards/2?atlOrigin=eyJpIjoiNmYxYjJiMmYwYzg1NGZkN2FlZmRlMzBlOTlhZTM3OTciLCJwIjoiaiJ9)


| #  | Title | User Story | Story Points |
|----|-------|------------|--------------|
| 1  | Single URL Summarization | “As a user, I want to paste a single URL…so that I can quickly get the main points.” | 3 |
| 2  | Document Upload | “As a student, I want to upload a text/PDF…so that I can get a summary of my notes.” | 5 |
| 3  | View Generated Summary | “As a user, I want to see the generated summary clearly…” | 2 |
| 4  | Navigation Bar | “As a user, I want to navigate the site easily…” | 1 |
| 5  | Create Account | “As a user, I want to sign up with email/password…” | 3 |
| 6  | User Login | “As a user, I want to log in…” | 2 |
| 7  | Compare Two Sources | “As a researcher, I want to input two sources…” | 8 |
| 8  | Formatted Summaries | “As a user, I want summaries with headings/bullets…” | 2 |
| 9  | Transcript Summarization | “As a student, I want to upload a transcript…” | 5 |
| 10 | Mobile-Friendly UI | “As a user, I want the website to work well on my phone…” | 8 |

---

## Backlog Ordering Rationale
- **Top Priority (1–3):** Core summarization functionality → MVP backbone  
- **Next (4–6):** Navigation + authentication → personalization  
- **Then (7–8):** Comparative summaries + formatting → differentiation & usability  
- **Later (9–10):** Extra-value features → versatility & mobile-first UX  

---

## Definition of Ready (DoR)
A backlog item is **ready for development** when:  
- Clear **title** and full **user story** (As a…, I want…, so that…)  
- Acceptance criteria included  
- Estimated with story points  
- Dependencies identified, no blockers  
- Testable & demonstrable outcome  

---

## Estimation
We used **Planning Poker** for team-based estimation.  

**Estimation Scale:**  
- **Small (1–3):** UI tasks, displaying summaries  
- **Medium (5):** File parsing, transcript processing  
- **Large (8):** Comparative summarization, mobile responsiveness  

**Estimated Backlog:**  
- Single URL Summarization → 3  
- Document Upload Summarization → 5  
- View Generated Summary → 2  
- Website Navigation → 1  
- User Account Creation → 3  
- User Login → 2  
- Compare Two Sources → 8  
- Formatted Summaries → 2  
- Transcript Summarization → 5  
- Mobile-Friendly UI → 8  

---

## 🚀 Tech Stack
- **Frontend:** TypeScript + Tailwind CSS  
- **Backend:** Django (Python)  
- **AI Model:** Hugging Face Transformers  
- **Database:** PostgreSQL  
- **Deployment:** Vercel (frontend), Render (backend)  


