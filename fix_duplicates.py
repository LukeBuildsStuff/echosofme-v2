#!/usr/bin/env python3
"""
Script to replace duplicate questions with new category-appropriate questions
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

def generate_new_questions_by_category():
    """Generate new questions for each category"""
    new_questions = {
        'relationships': [
            "How do you handle power dynamics in relationships?",
            "What role does vulnerability play in your relationships?",
            "How do you maintain your identity within a relationship?",
            "What's your approach to setting relationship boundaries?",
            "How do you handle different attachment styles in relationships?",
            "What does emotional safety mean to you in relationships?",
            "How do you navigate relationships with different communication styles?",
            "What's your experience with long-distance relationships?",
            "How do you handle relationship transitions and changes?",
            "What role does forgiveness play in your relationships?",
            "How do you balance independence and togetherness?",
            "What patterns do you notice in your relationship conflicts?",
            "How do you support a partner through difficult times?",
            "What's your approach to relationship maintenance?",
            "How do you handle different life goals in a relationship?",
            "What role does trust play in your relationships?",
            "How do you navigate financial discussions in relationships?",
            "What's your experience with blended families or complex family dynamics?",
            "How do you handle social pressure about your relationships?",
            "What relationship advice would you give to someone starting out?",
            "How do you know when a relationship is worth fighting for?",
            "What's your approach to relationship compromise?",
            "How do you handle different social needs in a relationship?",
            "What role does physical affection play in your relationships?",
            "How do you navigate relationships with different values?",
            "What's your experience with relationship counseling or therapy?",
            "How do you handle relationship insecurities?",
            "What's your approach to maintaining friendships while in a relationship?",
            "How do you handle different conflict resolution styles?",
            "What does mutual respect look like to you in relationships?",
            "How do you navigate cultural differences in relationships?",
            "What's your experience with relationship milestones?",
            "How do you handle different life phases in relationships?",
            "What role does shared humor play in your relationships?",
            "How do you maintain romance in long-term relationships?",
            "What's your approach to handling ex-partners and past relationships?",
            "How do you navigate relationships with different energy levels?",
            "What's your experience with relationship expectations vs reality?",
            "How do you handle different approaches to personal growth in relationships?",
            "What does partnership mean to you beyond romantic relationships?"
        ],
        'romantic_love': [
            "How has your understanding of romance evolved over time?",
            "What does falling in love feel like to you?",
            "How do you express romantic love?",
            "What role does physical chemistry play in romantic love?",
            "How do you know when romantic feelings are genuine?",
            "What's your experience with unrequited love?",
            "How do you maintain passion in long-term relationships?",
            "What does romantic compatibility mean to you?",
            "How do you handle the transition from passion to deep love?",
            "What role does romance play in everyday life?",
            "How do you navigate love and timing?",
            "What's your experience with first love?",
            "How do you balance romantic love with self-love?",
            "What does it mean to choose love daily?",
            "How do you handle romantic disappointment?",
            "What's your approach to romantic gestures?",
            "How do you know when you're ready for romantic love?",
            "What role does intellectual connection play in romantic love?",
            "How do you handle different love languages in romantic relationships?",
            "What's your experience with love at different life stages?"
        ],
        'professional': [
            "What does professional integrity mean to you?",
            "How do you handle workplace politics?",
            "What's your approach to professional networking?",
            "How do you balance ambition with ethics in your career?",
            "What role does mentorship play in your professional life?",
            "How do you handle professional setbacks?",
            "What's your approach to work-life integration?",
            "How do you stay current in your professional field?",
            "What does professional success look like to you?",
            "How do you handle difficult clients or customers?",
            "What's your experience with professional transitions?",
            "How do you approach professional skill development?",
            "What role does creativity play in your professional work?",
            "How do you handle professional competition?",
            "What's your approach to professional communication?",
            "How do you navigate professional relationships?",
            "What does professional leadership mean to you?",
            "How do you handle professional stress?",
            "What's your experience with professional failure?",
            "How do you approach professional goal setting?",
            "What role does collaboration play in your professional life?",
            "How do you handle professional criticism?",
            "What's your approach to professional presentations?",
            "How do you navigate professional hierarchies?",
            "What does professional authenticity mean to you?",
            "How do you handle professional burnout?",
            "What's your experience with professional recognition?",
            "How do you approach professional problem-solving?",
            "What role does innovation play in your professional work?",
            "How do you handle professional uncertainty?",
            "What's your approach to professional time management?",
            "How do you navigate professional ethics dilemmas?",
            "What does professional growth mean to you?",
            "How do you handle professional negotiations?",
            "What's your experience with professional teams?",
            "How do you approach professional decision-making?",
            "What role does technology play in your professional work?",
            "How do you handle professional deadlines?",
            "What's your approach to professional learning?"
        ],
        'marriage_partnerships': [
            "What does partnership equality mean to you?",
            "How do you handle major life decisions as a couple?",
            "What role does commitment play in your partnership?",
            "How do you navigate different career ambitions in a partnership?",
            "What's your approach to handling partnership stress?",
            "How do you maintain individual identity within a partnership?",
            "What does partnership support look like to you?",
            "How do you handle partnership financial planning?",
            "What role does shared vision play in your partnership?",
            "How do you navigate partnership family planning decisions?",
            "What's your approach to partnership conflict resolution?",
            "How do you handle partnership role distributions?",
            "What does partnership intimacy mean beyond physical connection?",
            "How do you maintain partnership friendship?",
            "What's your experience with partnership growth and change?",
            "How do you handle partnership social obligations?",
            "What role does partnership ritual and tradition play?",
            "How do you navigate partnership living arrangements?",
            "What's your approach to partnership communication?",
            "How do you handle partnership extended family relationships?",
            "What does partnership loyalty mean to you?",
            "How do you maintain partnership excitement and novelty?",
            "What's your experience with partnership challenges?"
        ],
        'philosophy_values': [
            "What does authentic living mean to you?",
            "How do you define personal responsibility?",
            "What role does hope play in your worldview?",
            "How do you approach the concept of truth?",
            "What does it mean to live with integrity?",
            "How do you handle moral complexity?",
            "What's your philosophy on personal change?",
            "How do you think about freedom and constraints?",
            "What role does tradition play in shaping values?",
            "How do you approach the concept of justice?",
            "What does it mean to live meaningfully?",
            "How do you handle value conflicts?",
            "What's your approach to making ethical choices?",
            "How do you think about individual vs collective good?",
            "What role does courage play in living your values?",
            "How do you approach the concept of forgiveness?",
            "What does personal growth mean to you?",
            "How do you handle uncertainty about values?",
            "What's your philosophy on human potential?",
            "How do you think about legacy and impact?",
            "What role does compassion play in your value system?",
            "How do you approach the concept of fairness?",
            "What does it mean to live with purpose?",
            "How do you handle competing values?",
            "What's your approach to moral decision-making?",
            "How do you think about good and evil?",
            "What role does wisdom play in your life philosophy?",
            "How do you approach the concept of sacrifice?",
            "What does inner peace mean to you?",
            "How do you handle moral uncertainty?",
            "What's your philosophy on personal boundaries?",
            "How do you think about duty and obligation?",
            "What role does humility play in your value system?",
            "How do you approach the concept of strength?",
            "What does it mean to live authentically?",
            "How do you handle value evolution over time?",
            "What's your approach to making principled stands?",
            "How do you think about loyalty and commitment?",
            "What role does gratitude play in your philosophy?",
            "How do you approach life's fundamental questions?",
            "What does moral courage mean to you?",
            "How do you handle philosophical disagreements?",
            "What's your approach to finding meaning in suffering?",
            "How do you think about personal freedom?",
            "What role does love play in your value system?",
            "How do you approach the concept of happiness?",
            "What does it mean to live with dignity?",
            "How do you handle moral ambiguity?",
            "What's your philosophy on personal relationships?",
            "How do you think about time and mortality?",
            "What role does truth play in your decision-making?",
            "How do you approach the concept of virtue?",
            "What does it mean to live with compassion?",
            "How do you handle value-based challenges?",
            "What's your approach to personal ethics?",
            "How do you think about honor and reputation?",
            "What role does empathy play in your worldview?",
            "How do you approach the concept of wisdom?",
            "What does it mean to live with purpose and meaning?",
            "How do you handle philosophical uncertainty?",
            "What's your approach to moral leadership?",
            "How do you think about personal and social responsibility?",
            "What role does faith play in your value system?",
            "How do you approach the concept of redemption?",
            "What does it mean to live with grace?",
            "How do you handle ethical complexity?",
            "What's your philosophy on human nature and potential?",
            "How do you think about justice and mercy?",
            "What role does character play in your life philosophy?",
            "How do you approach the concept of moral growth?",
            "What does it mean to live with authenticity and truth?",
            "How do you handle value-based conflicts with others?",
            "What's your approach to finding purpose in adversity?",
            "How do you think about personal and universal values?",
            "What role does service play in your value system?",
            "How do you approach the concept of inner strength?",
            "What does it mean to live with moral clarity?",
            "How do you handle the tension between ideals and reality?",
            "What's your philosophy on personal transformation?",
            "How do you think about responsibility to future generations?",
            "What role does integrity play in difficult decisions?",
            "How do you approach the concept of spiritual growth?",
            "What does it mean to live with authentic purpose?",
            "How do you handle moral courage in challenging situations?",
            "What's your approach to finding meaning in everyday life?",
            "How do you think about the relationship between values and actions?",
            "What role does moral imagination play in your decision-making?",
            "How do you approach the concept of living with honor?",
            "What does it mean to align your life with your deepest values?",
            "How do you handle the complexity of modern ethical challenges?",
            "What's your philosophy on personal responsibility in community?",
            "How do you think about the balance between self-care and service?",
            "What role does moral conviction play in your life choices?",
            "How do you approach the concept of living with purpose and passion?",
            "What does it mean to create a life of meaning and significance?",
            "How do you handle the ongoing work of moral and personal development?"
        ],
        'family_parenting': [
            "How do you balance individual needs with family harmony?",
            "What family communication patterns do you want to change?",
            "How do you handle different parenting philosophies in your family?",
            "What role does extended family play in your parenting decisions?",
            "How do you create family memories and traditions?",
            "What's your approach to teaching values to children?",
            "How do you handle family financial discussions?",
            "What family boundaries are most important to you?",
            "How do you navigate different family personalities?",
            "What's your experience with family celebrations and holidays?",
            "How do you handle family crisis and difficult times?",
            "What role does family history play in your current family?",
            "How do you create a sense of family identity?",
            "What's your approach to family decision-making?",
            "How do you handle family technology and screen time?",
            "What family activities bring you the most joy?",
            "How do you navigate family cultural and generational differences?",
            "What's your experience with family discipline and boundaries?",
            "How do you create family emotional safety?",
            "What role does family spirituality or values play?",
            "How do you handle family health and wellness?",
            "What's your approach to family learning and education?",
            "How do you navigate family work-life balance?",
            "What family legacy do you want to create?",
            "How do you handle family changes and transitions?",
            "What's your experience with family travel and adventures?",
            "How do you create family connection in busy times?",
            "What role does family service and giving play?",
            "How do you handle family disagreements about values?",
            "What's your approach to family problem-solving?",
            "How do you navigate family social relationships?",
            "What family strengths do you want to build on?",
            "How do you handle family stress and challenges?",
            "What's your experience with family creativity and play?",
            "How do you create family rituals and routines?",
            "What role does family storytelling play?",
            "How do you handle family expectations and pressure?",
            "What's your approach to family goal-setting?",
            "How do you navigate family independence and connection?",
            "What family values are you most passionate about passing on?",
            "How do you handle family conflict resolution?",
            "What's your experience with family growth and change?",
            "How do you create family fun and enjoyment?",
            "What role does family support play during challenges?",
            "How do you handle family different needs and preferences?",
            "What's your approach to family community involvement?",
            "How do you navigate family privacy and openness?",
            "What family achievements are you most proud of?",
            "How do you handle family disappointments?",
            "What's your experience with creating family culture?",
            "How do you balance family time with personal time?",
            "What role does family adventure and exploration play?",
            "How do you handle family responsibility distribution?",
            "What's your approach to family emotional expression?",
            "How do you navigate family different communication styles?",
            "What family memories do you most want to create?",
            "How do you handle family change and adaptation?",
            "What's your experience with family learning and growth?",
            "How do you create family belonging and acceptance?",
            "What role does family humor and laughter play?",
            "How do you handle family different life stages?",
            "What's your approach to family resilience building?",
            "How do you navigate family individual and collective needs?",
            "What family strengths do you see in challenging times?",
            "How do you handle family future planning?",
            "What's your experience with family gratitude and appreciation?",
            "How do you create family meaning and purpose?",
            "What role does family love and affection play?",
            "How do you handle family growth and development?",
            "What's your approach to family celebration and recognition?"
        ],
        'creative_expression': [
            "How does creative expression connect you to your authentic self?",
            "What role does creative experimentation play in your life?",
            "How do you use creativity to process emotions?",
            "What's your relationship with creative perfectionism?",
            "How does creative expression help you communicate?",
            "What role does creative community play in your expression?",
            "How do you handle creative vulnerability?",
            "What's your experience with creative flow states?",
            "How does creative expression impact your daily life?",
            "What role does creative tradition play in your expression?",
            "How do you use creativity for personal healing?",
            "What's your approach to creative collaboration?",
            "How does creative expression connect you to others?",
            "What role does creative spontaneity play in your life?",
            "How do you handle creative comparison with others?",
            "What's your experience with creative breakthroughs?",
            "How does creative expression help you understand yourself?",
            "What role does creative practice play in your routine?",
            "How do you use creativity to solve problems?",
            "What's your approach to creative goal-setting?",
            "How does creative expression impact your relationships?",
            "What role does creative inspiration play in your life?",
            "How do you handle creative plateaus?",
            "What's your experience with creative transformation?",
            "How does creative expression connect you to beauty?",
            "What role does creative discipline play in your practice?",
            "How do you use creativity to explore identity?",
            "What's your approach to creative sharing and showing?",
            "How does creative expression help you process life experiences?",
            "What role does creative play have in your adult life?",
            "How do you handle creative overwhelm?",
            "What's your experience with creative meditation or mindfulness?",
            "How does creative expression connect you to nature?",
            "What role does creative storytelling play in your life?",
            "How do you use creativity to build confidence?",
            "What's your approach to creative skill development?",
            "How does creative expression help you connect with culture?",
            "What role does creative curiosity play in your exploration?",
            "How do you handle creative energy management?",
            "What's your experience with creative therapeutic processes?",
            "How does creative expression impact your worldview?",
            "What role does creative celebration play in your life?",
            "How do you use creativity to explore spirituality?",
            "What's your approach to creative boundary-setting?",
            "How does creative expression help you process grief or loss?",
            "What role does creative adventure play in your exploration?",
            "How do you handle creative self-doubt?",
            "What's your experience with creative mentorship?",
            "How does creative expression connect you to joy?",
            "What role does creative ritual play in your practice?",
            "How do you use creativity to explore relationships?",
            "What's your approach to creative time management?",
            "How does creative expression help you find meaning?",
            "What role does creative innovation play in your life?",
            "How do you handle creative technology integration?",
            "What's your experience with creative community building?",
            "How does creative expression impact your physical wellbeing?",
            "What role does creative legacy play in your expression?",
            "How do you use creativity to explore different perspectives?",
            "What's your approach to creative resource management?"
        ],
        'daily_life': [
            "How do you create micro-moments of joy in your day?",
            "What's your relationship with your daily environment?",
            "How do you handle daily decision fatigue?",
            "What role does routine play in your daily wellbeing?",
            "How do you integrate mindfulness into daily activities?",
            "What's your approach to daily energy management?",
            "How do you create daily boundaries between work and life?",
            "What daily practices help you feel grounded?",
            "How do you handle daily interruptions and unexpected events?",
            "What's your relationship with daily technology use?",
            "How do you create daily connection with others?",
            "What role does daily movement play in your life?",
            "How do you approach daily meal planning and eating?",
            "What's your daily approach to learning something new?",
            "How do you create daily moments of beauty?",
            "What daily habits support your mental health?",
            "How do you handle daily overwhelm?",
            "What's your approach to daily time boundaries?",
            "How do you create daily rituals that matter to you?",
            "What role does daily gratitude play in your routine?",
            "How do you handle daily social energy management?",
            "What's your daily approach to physical comfort?",
            "How do you create daily meaning in ordinary tasks?",
            "What daily practices help you stay present?",
            "How do you approach daily problem-solving?",
            "What's your relationship with daily planning vs spontaneity?",
            "How do you create daily connection with nature?",
            "What role does daily creativity play in your routine?",
            "How do you handle daily motivation challenges?",
            "What's your approach to daily self-care?",
            "How do you create daily learning opportunities?",
            "What daily practices help you transition between activities?",
            "How do you handle daily perfectionism?",
            "What's your relationship with daily productivity?",
            "How do you create daily moments of reflection?",
            "What role does daily service or helping others play?",
            "How do you approach daily stress management?",
            "What's your daily approach to physical wellness?",
            "How do you create daily connection with your values?",
            "What daily practices help you feel accomplished?",
            "How do you handle daily comparison with others?",
            "What's your approach to daily financial awareness?",
            "How do you create daily opportunities for growth?",
            "What role does daily humor play in your life?",
            "How do you approach daily relationship maintenance?",
            "What's your daily approach to information consumption?",
            "How do you create daily spaces for solitude?",
            "What daily practices help you feel connected to purpose?",
            "How do you handle daily transitions and changes?",
            "What's your approach to creating daily balance?"
        ],
        'friendships_social': [
            "How do you nurture friendships during life transitions?",
            "What's your approach to making adult friendships?",
            "How do you handle friendship misunderstandings?",
            "What role does friendship play in your personal growth?",
            "How do you balance friendship depth vs breadth?",
            "What's your experience with friendship across different life stages?",
            "How do you handle friendship geography and distance?",
            "What social situations energize you most?",
            "How do you approach friendship boundary conversations?",
            "What's your relationship with social media friendships?",
            "How do you handle friendship disappointment?",
            "What role does friendship play in your identity?",
            "How do you approach social anxiety or shyness?",
            "What's your experience with friendship loyalty?",
            "How do you handle friendship different values?",
            "What social activities bring out your best self?",
            "How do you approach friendship conflict resolution?",
            "What's your relationship with social expectations?",
            "How do you handle friendship jealousy or competition?",
            "What role does friendship play in your support system?",
            "How do you approach social energy management?",
            "What's your experience with friendship reciprocity?",
            "How do you handle social FOMO (fear of missing out)?",
            "What social settings challenge you most?",
            "How do you approach friendship different communication styles?",
            "What's your relationship with social introversion/extroversion?",
            "How do you handle friendship life phase differences?",
            "What role does friendship play in your mental health?",
            "How do you approach social networking and connections?",
            "What's your experience with friendship trust building?",
            "How do you handle social overwhelm?",
            "What social traditions or rituals matter most to you?",
            "How do you approach friendship maintenance over time?",
            "What's your relationship with social authenticity?",
            "How do you handle friendship different priorities?"
        ],
        'hypotheticals': [
            "If you could experience one day from history, which would you choose?",
            "Would you rather have perfect memory or perfect intuition?",
            "If you could solve one global problem instantly, what would it be?",
            "Would you choose to know your life's purpose or discover it gradually?",
            "If you could have dinner with your future self, what would you ask?",
            "Would you rather be able to speak all languages or play all instruments?",
            "If you could live in any book or movie world, which would it be?",
            "Would you choose immortality or a perfect but finite life?",
            "If you could change one historical event, what would it be?",
            "Would you rather have the ability to heal others or see the future?",
            "If you could master any field of study, what would you choose?",
            "Would you rather live without the internet or without books?",
            "If you could have a conversation with any animal, which would you choose?",
            "Would you choose to be famous or to live in complete anonymity?",
            "If you could eliminate one emotion from human experience, what would it be?",
            "Would you rather always tell the truth or always know when others are lying?",
            "If you could live in any era of human history, when would you choose?",
            "Would you choose to have children but be poor, or be wealthy but childless?",
            "If you could guarantee one thing about your future, what would it be?",
            "Would you rather be able to control time or control probability?",
            "If you could live anywhere in the universe, where would you choose?",
            "Would you choose to be the smartest person alive or the kindest?",
            "If you could undo one mistake from your past, would you?",
            "Would you rather have unlimited money or unlimited time?",
            "If you could change one thing about human nature, what would it be?",
            "Would you choose to be able to read minds or be invisible at will?",
            "If you could live in a world without any problems, would you?",
            "Would you rather be able to fly or breathe underwater?",
            "If you could know the answer to any one question, what would you ask?",
            "Would you choose a life of adventure or a life of peace?",
            "If you could have any fictional character as your best friend, who would it be?",
            "Would you rather never feel physical pain or never feel emotional pain?",
            "If you could change careers without any obstacles, what would you do?",
            "Would you choose to be extraordinarily talented in one area or good at everything?",
            "If you could bring back one extinct species, which would you choose?"
        ],
        'personal': [
            "What aspect of your personality surprises people most?",
            "How do you handle your own emotional contradictions?",
            "What personal pattern are you most aware of?",
            "How do you define your personal style?",
            "What's your relationship with your own ambition?",
            "How do you handle personal disappointment in yourself?",
            "What personal boundary is most important to you?",
            "How do you approach personal goal-setting?",
            "What aspect of yourself are you still discovering?",
            "How do you handle your own personal growth resistance?",
            "What personal ritual means the most to you?",
            "How do you approach personal decision-making?",
            "What personal strength took you longest to recognize?",
            "How do you handle personal vulnerability?",
            "What aspect of your personality has changed most over time?",
            "How do you approach personal reflection and introspection?",
            "What personal quality do you most want to develop?",
            "How do you handle personal failure or setbacks?",
            "What personal accomplishment are you most proud of?",
            "How do you approach personal authenticity?"
        ],
        'personal_history': [
            "What life experience first made you feel like an adult?",
            "Describe a moment when you realized you had changed significantly.",
            "What childhood belief about the world turned out to be completely wrong?",
            "Tell me about a time when you had to defend someone else.",
            "What's an experience that taught you about your own strength?",
            "Describe a moment when you felt truly understood by someone.",
            "What's a place from your past that you can still see clearly in your mind?",
            "Tell me about a time when you had to choose between safety and adventure.",
            "What's an experience that completely shifted your perspective on relationships?",
            "Describe a moment when you felt most connected to your heritage or culture.",
            "What's a time when you surprised yourself with your own resilience?",
            "Tell me about an experience that taught you about forgiveness.",
            "What's a moment from your past that still makes you laugh?",
            "Describe a time when you had to trust someone completely.",
            "What's an experience that taught you about loss or grief?",
            "Tell me about a moment when you felt most creative or inspired.",
            "What's a time when you had to stand up for your beliefs?",
            "Describe an experience that taught you about different ways of living.",
            "What's a moment when you felt most grateful for your life?",
            "Tell me about a time when you had to learn something difficult about yourself."
        ],
        'hobbies': [
            "How do your hobbies reflect your personality?",
            "What hobby taught you the most about patience?",
            "How do you approach learning new hobby skills?",
            "What's your relationship with hobby perfectionism?",
            "How do your hobbies connect you with others?",
            "What hobby helps you relax most effectively?",
            "How do you balance hobby time with other responsibilities?",
            "What's your approach to hobby equipment and tools?",
            "How do your hobbies challenge you?",
            "What role do hobbies play in your identity?",
            "How do you share your hobby knowledge with others?",
            "What's your experience with hobby communities?",
            "How do your hobbies inspire other areas of your life?",
            "What hobby would you like to turn into something more?",
            "How do your hobbies help you process stress?",
            "What's your approach to hobby goal-setting?",
            "How do your hobbies connect you to different cultures?",
            "What hobby gives you the greatest sense of accomplishment?",
            "How do you handle hobby frustration or plateaus?",
            "What's your relationship with seasonal or weather-dependent hobbies?"
        ],
        'education': [
            "How has your approach to learning evolved over time?",
            "What educational experience challenged your assumptions most?",
            "How do you handle learning something that doesn't come naturally?",
            "What's your relationship with educational failure or struggle?",
            "How do you choose what to learn outside formal education?",
            "What educational experience gave you the most confidence?",
            "How do you balance learning breadth vs depth?",
            "What's your approach to learning from people with different perspectives?",
            "How has technology changed your learning process?",
            "What educational goal are you currently pursuing?",
            "How do you handle learning in group vs individual settings?",
            "What's your experience with learning different types of skills?",
            "How do you apply what you learn to your daily life?",
            "What educational experience taught you most about yourself?",
            "How do you handle information overload in learning?",
            "What's your approach to unlearning incorrect information?",
            "How do you stay curious and motivated to learn?",
            "What educational resource has been most valuable to you?",
            "How do you handle learning outside your comfort zone?",
            "What would you most like to teach others?"
        ],
        'career': [
            "How do you define career fulfillment?",
            "What's your approach to career risk-taking?",
            "How do you handle career comparison with others?",
            "What career skill are you most proud of developing?",
            "How do you balance career ambition with personal values?",
            "What's your experience with career mentorship?",
            "How do you approach career networking authentically?",
            "What career challenge taught you the most?",
            "How do you handle career uncertainty?",
            "What's your relationship with career failure?",
            "How do you approach career goal-setting?",
            "What career accomplishment surprised you most?",
            "How do you handle career work-life integration?",
            "What's your approach to career skill development?",
            "How do you navigate career political dynamics?",
            "What career advice would you give your younger self?",
            "How do you approach career transition and change?",
            "What's your experience with career leadership?",
            "How do you handle career stress and pressure?",
            "What career legacy do you want to create?"
        ]
    }
    
    return new_questions

def replace_duplicates(questions, duplicates, new_questions_by_category):
    """Replace duplicate questions with new ones while preserving structure"""
    print(f"Processing {len(duplicates)} duplicate question types...")
    
    for question_text, occurrences in duplicates.items():
        # Keep the first occurrence, replace the rest
        occurrences_to_replace = occurrences[1:]  # Skip first occurrence
        
        print(f"\nReplacing {len(occurrences_to_replace)} duplicates of: '{question_text[:60]}...'")
        
        for i, occurrence in enumerate(occurrences_to_replace):
            category = occurrence['category']
            index = occurrence['index']
            
            # Get replacement questions for this category
            replacement_pool = new_questions_by_category.get(category, [])
            if not replacement_pool:
                print(f"  Warning: No replacement questions available for category '{category}'")
                continue
            
            # Select a random replacement question
            new_question = random.choice(replacement_pool)
            
            # Update the question
            questions[index]['question'] = new_question
            
            print(f"  [{category}] Replaced with: '{new_question[:60]}...'")
            
            # Remove the used question to avoid creating new duplicates
            replacement_pool.remove(new_question)
    
    return questions

def verify_no_duplicates(questions):
    """Verify no duplicate questions remain"""
    question_counts = Counter(q['question'] for q in questions)
    duplicates = {q: count for q, count in question_counts.items() if count > 1}
    
    if duplicates:
        print(f"\nWARNING: {len(duplicates)} duplicate questions still exist:")
        for q, count in duplicates.items():
            print(f"  {count}x: {q[:60]}...")
    else:
        print("\n✅ SUCCESS: No duplicate questions found!")
    
    return len(duplicates) == 0

def save_questions(questions, backup=True):
    """Save questions to file with optional backup"""
    if backup:
        # Create backup
        with open('/home/luke/echosofme-v2/src/data/questions.json.backup', 'w') as f:
            with open('/home/luke/echosofme-v2/src/data/questions.json', 'r') as original:
                f.write(original.read())
        print("✅ Created backup: questions.json.backup")
    
    # Save new questions
    with open('/home/luke/echosofme-v2/src/data/questions.json', 'w') as f:
        json.dump(questions, f, indent=2)
    print("✅ Saved updated questions.json")

def main():
    """Main function to process duplicate questions"""
    print("🔍 Loading questions...")
    questions = load_questions()
    print(f"Loaded {len(questions)} questions")
    
    print("\n🔍 Finding duplicates...")
    duplicates = find_duplicates(questions)
    print(f"Found {len(duplicates)} duplicate question types")
    
    # Calculate total duplicates to replace
    total_duplicates_to_replace = sum(len(occurrences) - 1 for occurrences in duplicates.values())
    print(f"Total duplicate instances to replace: {total_duplicates_to_replace}")
    
    if total_duplicates_to_replace == 0:
        print("✅ No duplicates to replace!")
        return
    
    print("\n📝 Generating replacement questions...")
    new_questions_by_category = generate_new_questions_by_category()
    
    # Show category breakdown
    print("\nCategories with available replacement questions:")
    for category, question_list in new_questions_by_category.items():
        print(f"  {category}: {len(question_list)} replacement questions")
    
    print("\n🔄 Replacing duplicate questions...")
    updated_questions = replace_duplicates(questions, duplicates, new_questions_by_category)
    
    print("\n🔍 Verifying results...")
    success = verify_no_duplicates(updated_questions)
    
    if success:
        print("\n💾 Saving results...")
        save_questions(updated_questions)
        print("\n🎉 Successfully replaced all duplicate questions!")
    else:
        print("\n❌ Some duplicates remain. Not saving changes.")

if __name__ == "__main__":
    main()