# FACS673 Team 2 - AI Summarizer

## Team Roster:

* **__Dhairya Shah**: Microservices developer
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
* **Data Persistence**: Store user summaries and history in a MySQL database.
* **Deployment**: The application will be deployed and accessible to a limited beta group via Vercel and Render.


## Stakeholders

* Students: Want to quickly grasp the main points of long articles, research papers, or lecture notes to save time while studying and preparing for exams. They need a tool to make their learning more efficient.
* Working Professionals: Seek to stay updated on industry trends, synthesize key takeaways from reports, and quickly digest meeting transcripts to make faster, more informed decisions.
* Researchers: Need to review and compare a large volume of academic papers to identify key findings, methodologies, and gaps in the literature. They require a tool to streamline their literature review process.





