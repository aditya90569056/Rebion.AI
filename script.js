// function locomotive() {
//   gsap.registerPlugin(ScrollTrigger);

//   const locoScroll = new LocomotiveScroll({
//     el: document.querySelector("#main"),
//     smooth: true ,
//   });
//   locoScroll.on("scroll", ScrollTrigger.update);

//   ScrollTrigger.scrollerProxy("#main", {
//     scrollTop(value) {
//       return arguments.length
//         ? locoScroll.scrollTo(value, 0, 0)
//         : locoScroll.scroll.instance.scroll.y;
//     },

//     getBoundingClientRect() {
//       return {
//         top: 0,
//         left: 0,
//         width: window.innerWidth,
//         height: window.innerHeight,
//       };
//     },

//     pinType: document.querySelector("#main").style.transform
//       ? "transform"
//       : "fixed",
//   });
//   ScrollTrigger.addEventListener("refresh", () => locoScroll.update());
//   ScrollTrigger.refresh();
// }
// locomotive();


// // const canvas = document.querySelector("canvas");
// // const context = canvas.getContext("2d");

// // canvas.width = window.innerWidth;
// // canvas.height = window.innerHeight;


// window.addEventListener("resize", function () {
//   canvas.width = window.innerWidth;
//   canvas.height = window.innerHeight;
//   render();
// });

// // function files(index) {
// //   var data = `
// //      ./male0001.png
// //      ./male0002.png
// //      ./male0003.png
// //      ./male0004.png
// //      ./male0005.png
// //      ./male0006.png
// //      ./male0007.png
// //      ./male0008.png
// //      ./male0009.png
// //      ./male0010.png
// //      ./male0011.png
// //      ./male0012.png
// //      ./male0013.png
// //      ./male0014.png
// //      ./male0015.png
// //      ./male0016.png
// //      ./male0017.png
// //      ./male0018.png
// //      ./male0019.png
// //      ./male0020.png
// //      ./male0021.png
// //      ./male0022.png
// //      ./male0023.png
// //      ./male0024.png
// //      ./male0025.png
// //      ./male0026.png
// //      ./male0027.png
// //      ./male0028.png
// //      ./male0029.png
// //      ./male0030.png
// //      ./male0031.png
// //      ./male0032.png
// //      ./male0033.png
// //      ./male0034.png
// //      ./male0035.png
// //      ./male0036.png
// //      ./male0037.png
// //      ./male0038.png
// //      ./male0039.png
// //      ./male0040.png
// //      ./male0041.png
// //      ./male0042.png
// //      ./male0043.png
// //      ./male0044.png
// //      ./male0045.png
// //      ./male0046.png
// //      ./male0047.png
// //      ./male0048.png
// //      ./male0049.png
// //      ./male0050.png
// //      ./male0051.png
// //      ./male0052.png
// //      ./male0053.png
// //      ./male0054.png
// //      ./male0055.png
// //      ./male0056.png
// //      ./male0057.png
// //      ./male0058.png
// //      ./male0059.png
// //      ./male0060.png
// //      ./male0061.png
// //      ./male0062.png
// //      ./male0063.png
// //      ./male0064.png
// //      ./male0065.png
// //      ./male0066.png
// //      ./male0067.png
// //      ./male0068.png
// //      ./male0069.png
// //      ./male0070.png
// //      ./male0071.png
// //      ./male0072.png
// //      ./male0073.png
// //      ./male0074.png
// //      ./male0075.png
// //      ./male0076.png
// //      ./male0077.png
// //      ./male0078.png
// //      ./male0079.png
// //      ./male0080.png
// //      ./male0081.png
// //      ./male0082.png
// //      ./male0083.png
// //      ./male0084.png
// //      ./male0085.png
// //      ./male0086.png
// //      ./male0087.png
// //      ./male0088.png
// //      ./male0089.png
// //      ./male0090.png
// //      ./male0091.png
// //      ./male0092.png
// //      ./male0093.png
// //      ./male0094.png
// //      ./male0095.png
// //      ./male0096.png
// //      ./male0097.png
// //      ./male0098.png
// //      ./male0099.png
// //      ./male0100.png
// //      ./male0101.png
// //      ./male0102.png
// //      ./male0103.png
// //      ./male0104.png
// //      ./male0105.png
// //      ./male0106.png
// //      ./male0107.png
// //      ./male0108.png
// //      ./male0109.png
// //      ./male0110.png
// //      ./male0111.png
// //      ./male0112.png
// //      ./male0113.png
// //      ./male0114.png
// //      ./male0115.png
// //      ./male0116.png
// //      ./male0117.png
// //      ./male0118.png
// //      ./male0119.png
// //      ./male0120.png
// //      ./male0121.png
// //      ./male0122.png
// //      ./male0123.png
// //      ./male0124.png
// //      ./male0125.png
// //      ./male0126.png
// //      ./male0127.png
// //      ./male0128.png
// //      ./male0129.png
// //      ./male0130.png
// //      ./male0131.png
// //      ./male0132.png
// //      ./male0133.png
// //      ./male0134.png
// //      ./male0135.png
// //      ./male0136.png
// //      ./male0137.png
// //      ./male0138.png
// //      ./male0139.png
// //      ./male0140.png
// //      ./male0141.png
// //      ./male0142.png
// //      ./male0143.png
// //      ./male0144.png
// //      ./male0145.png
// //      ./male0146.png
// //      ./male0147.png
// //      ./male0148.png
// //      ./male0149.png
// //      ./male0150.png
// //      ./male0151.png
// //      ./male0152.png
// //      ./male0153.png
// //      ./male0154.png
// //      ./male0155.png
// //      ./male0156.png
// //      ./male0157.png
// //      ./male0158.png
// //      ./male0159.png
// //      ./male0160.png
// //      ./male0161.png
// //      ./male0162.png
// //      ./male0163.png
// //      ./male0164.png
// //      ./male0165.png
// //      ./male0166.png
// //      ./male0167.png
// //      ./male0168.png
// //      ./male0169.png
// //      ./male0170.png
// //      ./male0171.png
// //      ./male0172.png
// //      ./male0173.png
// //      ./male0174.png
// //      ./male0175.png
// //      ./male0176.png
// //      ./male0177.png
// //      ./male0178.png
// //      ./male0179.png
// //      ./male0180.png
// //      ./male0181.png
// //      ./male0182.png
// //      ./male0183.png
// //      ./male0184.png
// //      ./male0185.png
// //      ./male0186.png
// //      ./male0187.png
// //      ./male0188.png
// //      ./male0189.png
// //      ./male0190.png
// //      ./male0191.png
// //      ./male0192.png
// //      ./male0193.png
// //      ./male0194.png
// //      ./male0195.png
// //      ./male0196.png
// //      ./male0197.png
// //      ./male0198.png
// //      ./male0199.png
// //      ./male0200.png
// //      ./male0201.png
// //      ./male0202.png
// //      ./male0203.png
// //      ./male0204.png
// //      ./male0205.png
// //      ./male0206.png
// //      ./male0207.png
// //      ./male0208.png
// //      ./male0209.png
// //      ./male0210.png
// //      ./male0211.png
// //      ./male0212.png
// //      ./male0213.png
// //      ./male0214.png
// //      ./male0215.png
// //      ./male0216.png
// //      ./male0217.png
// //      ./male0218.png
// //      ./male0219.png
// //      ./male0220.png
// //      ./male0221.png
// //      ./male0222.png
// //      ./male0223.png
// //      ./male0224.png
// //      ./male0225.png
// //      ./male0226.png
// //      ./male0227.png
// //      ./male0228.png
// //      ./male0229.png
// //      ./male0230.png
// //      ./male0231.png
// //      ./male0232.png
// //      ./male0233.png
// //      ./male0234.png
// //      ./male0235.png
// //      ./male0236.png
// //      ./male0237.png
// //      ./male0238.png
// //      ./male0239.png
// //      ./male0240.png
// //      ./male0241.png
// //      ./male0242.png
// //      ./male0243.png
// //      ./male0244.png
// //      ./male0245.png
// //      ./male0246.png
// //      ./male0247.png
// //      ./male0248.png
// //      ./male0249.png
// //      ./male0250.png
// //      ./male0251.png
// //      ./male0252.png
// //      ./male0253.png
// //      ./male0254.png
// //      ./male0255.png
// //      ./male0256.png
// //      ./male0257.png
// //      ./male0258.png
// //      ./male0259.png
// //      ./male0260.png
// //      ./male0261.png
// //      ./male0262.png
// //      ./male0263.png
// //      ./male0264.png
// //      ./male0265.png
// //      ./male0266.png
// //      ./male0267.png
// //      ./male0268.png
// //      ./male0269.png
// //      ./male0270.png
// //      ./male0271.png
// //      ./male0272.png
// //      ./male0273.png
// //      ./male0274.png
// //      ./male0275.png
// //      ./male0276.png
// //      ./male0277.png
// //      ./male0278.png
// //      ./male0279.png
// //      ./male0280.png
// //      ./male0281.png
// //      ./male0282.png
// //      ./male0283.png
// //      ./male0284.png
// //      ./male0285.png
// //      ./male0286.png
// //      ./male0287.png
// //      ./male0288.png
// //      ./male0289.png
// //      ./male0290.png
// //      ./male0291.png
// //      ./male0292.png
// //      ./male0293.png
// //      ./male0294.png
// //      ./male0295.png
// //      ./male0296.png
// //      ./male0297.png
// //      ./male0298.png
// //      ./male0299.png
// //      ./male0300.png
// //  `;
// //   return data.split("\n")[index];
// // }

// // const frameCount = 300;

// // const images = [];
// // const imageSeq = {
// //   frame: 1,
// // };

// // for (let i = 0; i < frameCount; i++) {
// //   const img = new Image();
// //   img.src = files(i);
// //   images.push(img);
// // }

// // gsap.to(imageSeq, {
// //   frame: frameCount - 1,
// //   snap: "frame",
// //   ease: `none`,
// //   scrollTrigger: {
// //     scrub: 0.15,
// //     trigger: `#page>canvas`,
// //     start: `top top`,
// //     end: `600% top`,
// //     scroller: `#main`,
// //   },
// //   onUpdate: render,
// // });

// // images[1].onload = render;

// // function render() {
// //   scaleImage(images[imageSeq.frame], context);
// // }

// function scaleImage(img, ctx) {
//   var canvas = ctx.canvas;
//   var hRatio = canvas.width / img.width;
//   var vRatio = canvas.height / img.height;
//   var ratio = Math.max(hRatio, vRatio);
//   var centerShift_x = (canvas.width - img.width * ratio) / 2;
//   var centerShift_y = (canvas.height - img.height * ratio) / 2;
//   ctx.clearRect(0, 0, canvas.width, canvas.height);
//   ctx.drawImage(
//     img,
//     0,
//     0,
//     img.width,
//     img.height,
//     centerShift_x,
//     centerShift_y,
//     img.width * ratio,
//     img.height * ratio
//   );
// }
// ScrollTrigger.create({
//   trigger: "#page>canvas",
//   pin: true,
//   // markers:true,
//   scroller: `#main`,
//   start: `top top`,
//   end: `600% top`,
// });



// gsap.to("#page1",{
//   scrollTrigger:{
//     trigger:`#page1`,
//     start:`top top`,
//     end:`bottom top`,
//     pin:true,
//     scroller:`#main`
//   }
// })
// gsap.to("#page2",{
//   scrollTrigger:{
//     trigger:`#page2`,
//     start:`top top`,
//     end:`bottom top`,
//     pin:true,
//     scroller:`#main`
//   }
// })
// gsap.to("#page3",{
//   scrollTrigger:{
//     trigger:`#page3`,
//     start:`top top`,
//     end:`bottom top`,
//     pin:true,
//     scroller:`#main`
//   }
// })
// // Nav
// const menuBtn = document.querySelector(".menu-btn");
// const navLinks = document.querySelector(".nav-links");

// menuBtn.addEventListener("click", () => {
//     navLinks.classList.toggle("active");
// });
    
// // loader
// const tl = gsap.timeline();

// tl.from(".glass-logo",{
//     scale:0.7,
//     opacity:0,
//     filter:"blur(20px)",
//     duration:1.5,
//     ease:"expo.out"
// })

// .to(".glass-logo",{
//     scale:1.15,
//     duration:1,
//     ease:"power2.inOut"
// })

// .to("#loader",{
//     scale:1.3,
//     opacity:0,
//     filter:"blur(30px)",
//     duration:1.2,
//     ease:"expo.inOut"
// })

// .set("#loader",{
//     display:"none"
// })

// .from(".hero h1",{
//     y:100,
//     opacity:0,
//     duration:1.2,
//     ease:"expo.out"
// },"-=0.5");
const counters = document.querySelectorAll(".counter");

const startCounter = (counter) => {

    const target = parseFloat(counter.dataset.target);
    const isDecimal = target % 1 !== 0;

    let current = 0;

    const increment = target / 120;

    const updateCounter = () => {

        current += increment;

        if(current >= target){

            if(isDecimal){
                counter.textContent = target.toFixed(1);
            }else{
                counter.textContent =
                    target.toLocaleString() + "+";
            }

            return;
        }

        if(isDecimal){
            counter.textContent =
                current.toFixed(1);
        }else{
            counter.textContent =
                Math.floor(current).toLocaleString();
        }

        requestAnimationFrame(updateCounter);
    };

    updateCounter();
};

const observer = new IntersectionObserver((entries)=>{

    entries.forEach(entry=>{

        if(entry.isIntersecting){

            startCounter(
                entry.target
            );

            observer.unobserve(
                entry.target
            );
        }

    });

});

counters.forEach(counter=>{
    observer.observe(counter);
});
const video = document.querySelector('.page3-bg-video');

video.addEventListener('mouseenter', () => {
    video.play();
});

video.addEventListener('mouseleave', () => {
    video.pause();
});
/* ============================
   REBION AI Chatbot (pre-answered Q&A)
   ============================ */
(function () {
    const widget = document.getElementById("chat-widget");
    const launcher = document.getElementById("down-arrow");
    const closeBtn = document.getElementById("chat-close");
    const body = document.getElementById("chat-body");
    const form = document.getElementById("chat-form");
    const input = document.getElementById("chat-input");
    const suggestions = document.getElementById("chat-suggestions");

    if (!widget || !launcher || !body) return;

const knowledgeBase = [
        // ---- Help & menu ----
        {
            keywords: ["help", "menu", "options", "what can u do", "what can you do"],
            answer: "I can answer questions about REBION AI's syllabus &amp; modules, podcasts &amp; episodes, services, research, contact details, social media and media gallery. Try asking 'tell me about the syllabus' or 'list the podcasts'."
        },
        // ---- Syllabus & modules ----
        {
            keywords: ["syllabus", "curriculum", "tracks", "modules", "what do you teach", "course list"],
            answer: "Our Core Concept Programme has Foundational AI + Biotech Tracks (7 modules): Foundations of Biological Data Analysis, Digital Agricultural &amp; Data Driven Farming, AI Decision Making in Biotech, Foundations of AI &amp; Machine Learning, Fundamentals of Drug Discovery &amp; Design, AI in Cyber Security and AI in Data Science. There are also Advanced Industry-Ready modules in Bioinformatics, Agritech, Bioprocess, Immunoinformatics, Vaccine Design, Medical Coding and more."
        },
        {
            keywords: ["biological data", "data analysis", "sequence analysis", "ncbi", "uniprot", "pdb", "blast", "fasta", "fastq", "linux", "sequence alignment"],
            answer: "Module: Foundations of Biological Data Analysis. You learn bioinformatics &amp; industry use cases, the Central Dogma, FASTA/FASTQ file structures, databases (NCBI, UniProt, PDB), Linux command line (grep, awk, sed), sequence alignment (global vs local) and BLAST hands-on (blastn, blastp, E-values, coverage) - ending with retrieving real gene &amp; protein sequences for a disease gene."
        },
        {
            keywords: ["agriculture", "farming", "agritech", "remote sensing", "crop prediction", "sustainable agriculture"],
            answer: "The Digital Agricultural &amp; Data Driven Farming track covers data-driven farming and agri-analytics; the advanced level is Predictive Modelling &amp; Remote Sensing in Agritech, plus Enterprise Scale AI for Sustainable Agriculture - building AI solutions from crop and satellite data."
        },
        {
            keywords: ["drug", "discovery", "molecular design", "virtual screening", "drug screening", "pharma"],
            answer: "Our syllabus includes Fundamentals of Drug Discovery &amp; Design and an advanced Deep Learning Based Virtual Drug Screening Platform. It's also the theme of our upcoming podcast EP 03 'AI in Drug Discovery', exploring ML algorithms for genomic sequence prediction and molecular design."
        },
        {
            keywords: ["machine learning", "deep learning", "artificial intelligence", "neural", "ai basics", "python"],
            answer: "Foundations of AI &amp; Machine Learning is our core intro track covering ML concepts, Python and modelling. From there you can go deeper with Advanced AI/ML for Scientific Application or Industry-Ready AI &amp; ML for R&amp;D and Analytics."
        },
        {
            keywords: ["cyber", "security", "hacking", "vulnerability"],
            answer: "Module: AI in Cyber Security - using artificial intelligence for threat detection, vulnerability analysis and securing modern research and organisational systems."
        },
        {
            keywords: ["data science", "statistics", "analytics", "visualisation", "visualization"],
            answer: "Module: AI in Data Science covers statistics, analytics and AI-driven insight generation, with a pathway into the NextGen AI &amp; Data Intelligence Program for deeper, industry-ready data engineering."
        },
        {
            keywords: ["advanced bioinformatics", "bioinformatics for r", "bioinfo", "pipeline", "computational biology"],
            answer: "At the advanced level we offer Advanced Bioinformatics &amp; Biological Data Analysis, Advance Bioinformatics for R&amp;D, and Computational Biology / Bioinformatics Pipeline Engineering - building production-grade analysis pipelines for research labs and industry."
        },
        {
            keywords: ["epitope", "antigen", "immunoinformatics", "immunology", "vaccine"],
            answer: "Tracks such as Epitope Prediction &amp; Antigen Design Using AI, Computational Immunology for NextGen Vaccine and AI Powered Vaccine Development for Biopharma cover AI-driven vaccine and immunology research, from epitopes all the way to industry-scale vaccine pipelines."
        },
        {
            keywords: ["bioprocess", "bioproduct", "optimization", "industrial biotech", "biopharma"],
            answer: "AI Powered Bioprocess &amp; Product Optimization and AI Solutions for Biopharma &amp; Industrial Biotech use AI to optimise fermentation, bioprocessing and industrial biotech products."
        },
        {
            keywords: ["medical coding", "anatomy", "terminology", "health informatics"],
            answer: "Medical Coding, Terminology &amp; Human Anatomy is an industry module covering healthcare coding systems and medical terminology - ideal for careers in health informatics and clinical data."
        },
        {
            keywords: ["biological languages", "protein language", "genome language"],
            answer: "Biological Languages treats DNA, RNA and protein sequences as languages for AI models - the foundation for sequence-based machine learning like protein language models."
        },
        {
            keywords: ["certificate", "certification", "completion"],
            answer: "Participants receive completion certificates for our training programs, workshops and camps. Contact us to confirm assessment and certificate details for your specific program."
        },
        {
            keywords: ["duration", "how long", "weeks", "days", "months", "schedule", "timing"],
            answer: "Foundation tracks are structured in week-wise modules (e.g. Week 1: Bio Foundations, Week 2: Python for Bio &amp; Stats) with day-wise lessons, while workshops and camps run over 1-2 days. Exact schedules are shared at registration."
        },
        // ---- Podcasts ----
        {
            keywords: ["podcast", "episodes", "episode", "guest", "speaker", "ep 01", "ep 02", "ep 03", "listen"],
            answer: "Current episodes: EP 01 'Journey of Dr. K.P. Singh' (25 July 2026, 52 min) and EP 02 'From Research to Patent Filing' with Dr. Atul Khajuria (29 July 2026, 45 min). EP 03 'AI in Drug Discovery' is coming soon. All are on the <a href='podcase.html'>Podcasts</a> page and YouTube."
        },
        {
            keywords: ["patent", "intellectual property", "patent filing", "commercialization", "startup", "ip rights"],
            answer: "Our featured episode EP 02 with Dr. Atul Khajuria ('From Research to Patent Filing', 29 July 2026) explains how lab breakthroughs become intellectual property, commercial patents and scalable biotech startups. Watch: <a href='https://youtu.be/MvH_GROD-t8'>youtu.be/MvH_GROD-t8</a>."
        },
        {
            keywords: ["kp singh", "dr. k.p", "dr k.p", "associate professor", "iit aspirants"],
            answer: "Dr. K.P. Singh is an Associate Professor and mentor featured in EP 01 'Journey of Dr. K.P. Singh' (25 July 2026) - from mentoring IIT aspirants to driving scientific innovation and education. Watch: <a href='https://youtu.be/i3cqExp2cpE'>youtu.be/i3cqExp2cpE</a>."
        },
        {
            keywords: ["khajuria", "atul"],
            answer: "Dr. Atul Khajuria joins us in EP 02 'From Research to Patent Filing' (29 July 2026) to guide researchers through turning scientific discoveries into intellectual property and patents. Watch: <a href='https://youtu.be/MvH_GROD-t8'>youtu.be/MvH_GROD-t8</a>."
        },
        {
            keywords: ["hiv", "protease", "cracking hiv"],
            answer: "We feature 'Cracking HIV: An IITian's Journey into HIV Protease Research' - a podcast and social video following a researcher's path into HIV protease research. Watch: <a href='https://youtu.be/i3cqExp2cpE'>youtu.be/i3cqExp2cpE</a>."
        },
        {
            keywords: ["phd", "ph.d", "research scholar", "phd students"],
            answer: "Check out our video '7 Problems Faced by PhD Students &amp; How to Tackle Them' on the Social page - practical, candid guidance for PhD students and scholars. Watch: <a href='https://youtu.be/-kgulSq_9Bg'>youtu.be/-kgulSq_9Bg</a>."
        },
        // ---- Contact ----
        {
            keywords: ["email id", "email address", "e mail", "mail us", "send email", "your email"],
            answer: "Our email address is <strong>info@rebioin.com</strong>. Write to us with any query and our team will get back to you."
        },
        {
            keywords: ["phone number", "contact number", "mobile", "call us", "telephone", "number"],
            answer: "You can call or WhatsApp us at <strong>+91 74040-681800</strong>."
        },
        {
            keywords: ["where are you", "office address", "located", "headquarter", "dehradun", "address of"],
            answer: "Our headquarters are at <strong>171, 3rd Floor, HDFC Bank, Vasant Vihar Branch, Dehradun - 248006</strong>."
        },
        {
            keywords: ["contact", "phone", "email", "reach", "address", "location", "call", "enquiry", "query", "talk to"],
            answer: "You can reach REBION AI at: email <strong>info@rebioin.com</strong>, phone <strong>+91 74040-681800</strong>. Our headquarters are at <strong>171, 3rd Floor, HDFC Bank, Vasant Vihar Branch, Dehradun - 248006</strong>. You can also send a message on the <a href='contact.html'>Contact Us</a> page."
        },
        // ---- Social & media ----
        {
            keywords: ["social", "instagram", "youtube", "follow", "reel", "channel", "social media"],
            answer: "Find us as <strong>@RebioinAI</strong> on YouTube (podcasts, talks and research content) and Instagram (reels, updates and highlights). Our tagline: 'Silence self doubt. Let AI amplify your potential.' All links are on the <a href='social.html'>Social</a> page."
        },
        {
            keywords: ["gallery", "media", "photo", "photos", "image", "images", "pictures"],
            answer: "Our media gallery has photos from workshops (AI in Biotechnology, the 2-Day Drug Discovery using AI/ML), laboratory skill camps, mushroom cultivation, awards and SBS University visits. Browse them on the <a href='gallery.html'>Media</a> page."
        },
        {
            keywords: ["sbs university", "rayat-bahra", "university visit"],
            answer: "We've held hands-on training and academic outreach at SBS University, plus workshops at Rayat-Bahra University - photos from these visits are in the Media gallery."
        },
        // ---- Programs, workshops, admissions ----
        {
            keywords: ["ai in biotechnology", "biotech workshop", "ai workshop", "workshop 2026", "drug discovery workshop"],
            answer: "'AI in Biotechnology Workshop 2026' is a hands-on workshop on machine learning for life sciences - working with biological datasets, sequence analysis, prediction models and mini-projects. Our '2 Day Workshop: Drug Discovery using AI/ML' covers AI in molecular design; photos from both are in the <a href='gallery.html'>Media</a> gallery."
        },
        {
            keywords: ["workshop", "workshops", "training program", "skill camp", "camp"],
            answer: "We run workshops like 'AI in Biotechnology Workshop 2026', the '2 Day Workshop: Drug Discovery using AI/ML', a Laboratory Skill Development Camp and hands-on training sessions. For dates and registration, contact us."
        },
        {
            keywords: ["bioinformatics training", "training program", "open for admission", "program open"],
            answer: "The Bioinformatics Training Program is open for applications - a structured, hands-on program covering biological sequence data, tools &amp; databases, Python for biological analysis and research-grade reporting. More details on the <a href='blog-bioinformatics.html'>announcement</a>."
        },
        {
            keywords: ["register", "registration", "admission", "apply", "enroll", "join", "seat"],
            answer: "Registrations are on a first-come, first-served basis. Latest openings include the Bioinformatics Training Program and Industry Internships. Contact <strong>info@rebioin.com</strong> or <strong>+91 74040-681800</strong> to apply."
        },
        {
            keywords: ["fee", "fees", "price", "pricing", "cost", "charge", "payment"],
            answer: "Fees depend on the program you choose. For accurate pricing of a specific module, workshop or camp, contact us at <strong>info@rebioin.com</strong>."
        },
        {
            keywords: ["placement", "job", "career", "internship", "hiring", "recruit"],
            answer: "Industry Internship Applications are open. Internships include live projects, mentorship, a completion certificate and networking. We also support placement preparation and career development - ask about the Career Development services."
        },
        // ---- Services, research, about ----
        {
            keywords: ["service", "services", "offer", "provide", "solutions", "what do you do"],
            answer: "Our services: Biotechnology Training, AI &amp; Bioinformatics solutions, Research Support (publications, data analysis, scientific writing), Industrial Workshops, Career Development and Institutional Collaboration with colleges and universities."
        },
        {
            keywords: ["research", "genomic", "genomics", "bioinformatics", "computational biology", "publication", "scientific writing"],
            answer: "In research we support genomic analysis, machine learning applications, computational biology, publications and scientific writing - and our advanced tracks cover Bioinformatics for R&amp;D and Virtual Drug Screening."
        },
        {
            keywords: ["mission", "vision", "about rebion", "what is rebion", "who are you", "company"],
            answer: "REBION AI bridges biological sciences and artificial intelligence to shape the future of biotechnology - training students, supporting research and building AI for tomorrow's leaders."
        },
        // ---- Basic chat ----
        {
            keywords: ["hi", "hello", "hey", "namaste", "greetings"],
            answer: "Hello! &#128075; I'm the REBION AI assistant. Ask me about the syllabus &amp; modules, podcasts, workshops, services, research or how to contact us."
        },
        {
            keywords: ["thanks", "thank", "thankyou", "ok", "great", "nice"],
            answer: "You're welcome! &#128522; Anything else you'd like to know about REBION AI?"
        }
    ];

    const fallbacks = [
        "I'm not sure about that yet. Try asking about the syllabus, podcasts, workshops, contact details or social media.",
        "I don't have that answer right now. You can ask about modules, podcasts, services or how to reach us.",
        "Hmm, I couldn't find a match. Ask me about the syllabus, podcasts, research, services or contact."
    ];

function findAnswer(text) {
        const query = text.toLowerCase();
        let best = null;
        let bestScore = 0;

        knowledgeBase.forEach(function (entry) {
            let score = 0;
            entry.keywords.forEach(function (word) {
                if (query.indexOf(word) !== -1) score += word.length;
            });
            if (score > bestScore) {
                bestScore = score;
                best = entry;
            }
        });

        if (best) return best.answer;
        return fallbacks[Math.floor(Math.random() * fallbacks.length)];
    }

    function addMessage(text, sender) {
        const wrap = document.createElement("div");
        wrap.className = "chat-message " + sender;

        if (sender === "bot") {
            const avatar = document.createElement("img");
            avatar.src = "male0145.png";
            avatar.alt = "";
            avatar.className = "msg-avatar";
            wrap.appendChild(avatar);
        }

        const bubble = document.createElement("div");
        bubble.className = "bubble";
        bubble.innerHTML = text;
        wrap.appendChild(bubble);

        body.appendChild(wrap);
        body.scrollTop = body.scrollHeight;
    }

    function showTyping() {
        const wrap = document.createElement("div");
        wrap.className = "chat-message bot";
        wrap.id = "chat-typing";

        const avatar = document.createElement("img");
        avatar.src = "male0145.png";
        avatar.alt = "";
        avatar.className = "msg-avatar";
        wrap.appendChild(avatar);

        const bubble = document.createElement("div");
        bubble.className = "bubble typing";
        bubble.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
        wrap.appendChild(bubble);

        body.appendChild(wrap);
        body.scrollTop = body.scrollHeight;
    }

    function removeTyping() {
        const typing = document.getElementById("chat-typing");
        if (typing) typing.remove();
    }

    function respond(question) {
        addMessage(question, "user");
        if (suggestions) suggestions.style.display = "none";
        showTyping();

        setTimeout(function () {
            removeTyping();
            addMessage(findAnswer(question), "bot");
        }, 650);
    }

    function openChat() {
        widget.classList.add("open");
        widget.setAttribute("aria-hidden", "false");
        launcher.classList.add("chat-active");
        if (input) input.focus();
    }

    function closeChat() {
        widget.classList.remove("open");
        widget.setAttribute("aria-hidden", "true");
        launcher.classList.remove("chat-active");
    }

    launcher.addEventListener("click", openChat);
    launcher.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            openChat();
        }
    });

    if (closeBtn) closeBtn.addEventListener("click", closeChat);

    if (form) {
        form.addEventListener("submit", function (e) {
            e.preventDefault();
            const text = input.value.trim();
            if (!text) return;
            input.value = "";
            respond(text);
        });
    }

    if (suggestions) {
        suggestions.addEventListener("click", function (e) {
            const btn = e.target.closest("button[data-q]");
            if (!btn) return;
            respond(btn.getAttribute("data-q"));
        });
    }
})();
