import fs from 'fs';
import path from 'path';

// Find all question files
function findQuestionFiles(dir) {
  const files = [];
  
  function searchDir(currentDir) {
    try {
      const entries = fs.readdirSync(currentDir);
      
      entries.forEach(entry => {
        const fullPath = path.join(currentDir, entry);
        const stats = fs.statSync(fullPath);
        
        if (stats.isDirectory()) {
          searchDir(fullPath);
        } else if (entry.includes('questions') && entry.endsWith('.json')) {
          files.push(fullPath);
        }
      });
    } catch (err) {
      // Skip directories we can't read
    }
  }
  
  searchDir(dir);
  return files;
}

async function consolidateQuestions() {
  console.log('🔍 Finding question files...');
  const questionFiles = findQuestionFiles('/home/luke');
  console.log(`📁 Found ${questionFiles.length} question files`);
  
  const allQuestions = [];
  const seenIds = new Set();
  
  for (const filePath of questionFiles) {
    try {
      console.log(`📖 Processing: ${path.basename(filePath)}`);
      const content = fs.readFileSync(filePath, 'utf8');
      const questions = JSON.parse(content);
      
      if (Array.isArray(questions)) {
        questions.forEach(question => {
          if (question.id && question.question && !seenIds.has(question.id)) {
            seenIds.add(question.id);
            allQuestions.push({
              id: question.id,
              question: question.question || question.question_text,
              category: question.category || 'general',
              source: path.basename(filePath)
            });
          }
        });
      }
    } catch (err) {
      console.warn(`⚠️  Error reading ${filePath}: ${err.message}`);
    }
  }
  
  console.log(`✨ Consolidated ${allQuestions.length} unique questions`);
  
  // Sort by category and id
  allQuestions.sort((a, b) => {
    if (a.category !== b.category) {
      return a.category.localeCompare(b.category);
    }
    return a.id - b.id;
  });
  
  // Write consolidated file
  const outputPath = '/home/luke/echosofme-v2/src/data/questions.json';
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, JSON.stringify(allQuestions, null, 2));
  
  // Generate categories summary
  const categories = {};
  allQuestions.forEach(q => {
    categories[q.category] = (categories[q.category] || 0) + 1;
  });
  
  console.log('\n📊 Categories breakdown:');
  Object.entries(categories)
    .sort(([,a], [,b]) => b - a)
    .forEach(([category, count]) => {
      console.log(`   ${category}: ${count} questions`);
    });
  
  console.log(`\n✅ Questions saved to: ${outputPath}`);
  return allQuestions.length;
}

// Run the consolidation
consolidateQuestions()
  .then(count => {
    console.log(`\n🎉 Successfully consolidated ${count} questions!`);
    process.exit(0);
  })
  .catch(err => {
    console.error('❌ Error:', err);
    process.exit(1);
  });