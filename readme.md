# autograder

This project contains several different scripts and credit should be given to a number of sources. Also, the files are often updated, 
so please check this file again when updates are made. For questions, please contact Ryan Spring (see sources below for contact information or contact through gitHub username = "springuistics")

The license for this tool is as follows:
The SpaCy-based Multiple Complexity Calculator (SMCC) and several of its components are text analysis programs. Please give credit where due:

This program is free software that may be freely redistributed and/or modified under the terms of the GNU General Public License.

This program and its components are distributed as a service to the general public, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.


---Files Explanation---
--1. <main.py>--
This is actually NOT the SMCC, but an earlier iteration that mainly relies on two previous works, as detailed below:

Executes a modified version of Lu's (2012) Lexical Complexity Analyzer that uses NLTK, SpaCy (Honnibal & Montani, 2017) to parse and POS tag individual text files
or batches of text files. The program also uses Lu's (2012) original counting system, but files should be pre-parsed for this portion of the code to be reliable. 
The program writes all of these counts to a single CSV file for comparative purposes, as reported in Spring and Johnson (2022). If you will use data from this 
portion of the code, please be sure to cute Lu (2012) and Spring and Johnson (20229.

The program also execute's Lu's (2010) L2 Syntactic Complexity Anlayzer (L2SCA). This program calls the 2003 Stanford Parser, and therefore requires that
the Java Developer Kit be installed. For details, please see the website for the L2SCA, below. If you will use data from this portion of the code, please
cite Lu (2010). Please be aware that if you do not have the Java Devloper Kit installed, main.py will fail and you cannot retrieve ANY data.


Links to original programs:
1. L2SCA - the L2 Syntactic Complexity Analyzer 3.3.3
found here: http://www.personal.psu.edu/xxl13/downloads/l2sca.html

2. LCA - the Lexical Complexity Analyzer
found here: http://www.personal.psu.edu/xxl13/downloads/lca.html


Citation:
Lu, X. (2010). Automatic analysis of syntactic complexity in second language writing. International Journal of Corpus Linguistics, 15(4), 474–496. https://doi.org/10.1075/ijcl.15.4.02lu

Lu, X. (2012). The relationship of lexical richness to the quality of ESL learners’ oral narratives. The Modern Language Journal, 96(2), 190-208.

Spring, R., & Johnson, M.W. (2022). The possibility of improving automated calculation of measures of lexical richness for EFL writing: A comparison of the LCA, NLTK, and SpaCy tools. System, 106, 770-786. https://doi.org/10.1016/j.system.2022.102770

## How to Use

Command line:
`python3 ./main.py ./input_data/<filename.txt>`

Example:
`python3 ./main.py ./input_data/moon.txt`



--2. <spacy_full.py>--
This is the SpaCy-based Multiple Complexity Calculator (SMCC). We recommend using this if you have difficulty running "main.py" especially due to difficulty with
the Java Developer Kit. The advantage to this program is that it currently only requires Python and SpaCy to be installed. 

This program takes individual or batches of text files and exports data about them into a csv file. The data provided about each text file is as follows:

1. Several measures of Lexical Complexity based on the modification to Lu's (2012) tool as outlined in Spring and Johnson (2022). However, these measurs are ONLY
the SpaCy based measures, as these are the measures that we found to be most correlated with both L2 proficiency and human-rating in our data set. If using this 
data, please besure to cite Lu (2012) and Spring and Johnson (20229.

2. Sevreal measures of Syntactic Complexity based on the ClearNLP tags. This section is currently under review and modification, but we will provide sources to cite
soon. In the meantime, we recommend looking at Lu's (2010) L2SCA for composite measures of syntacic complexity and Kyle and Crossley's (2017) TAASSC for fine-grained
measures. The measures currently provided as of June 1st, 2022 include those from Lu (2010) but based on ClearNLP tagging, and also several fine-grained measures,
that are not included in TAASSC, although it does not include usage-based verb-argument construction (VAC) measures like TAASSC. 

3. Several measures of Argument Words. This is currently under review and investigation and will be reported on again with areas to cite.

Link to TAASSC:
https://github.com/kristopherkyle/TAASSC

Link to Lu's Programs:
*See the links provided under the explanation of main.py

Citations:
u, X. (2010). Automatic analysis of syntactic complexity in second language writing. International Journal of Corpus Linguistics, 15(4), 474–496. https://doi.org/10.1075/ijcl.15.4.02lu

Lu, X. (2012). The relationship of lexical richness to the quality of ESL learners’ oral narratives. The Modern Language Journal, 96(2), 190-208.

Kyle, K., & Crossley, S. A. (2018). Measuring syntactic complexity in L2 writing using fine-grained clausal and phrasal indices. Modern Language Journal, 102(2), 333–349.

Spring, R., & Johnson, M.W. (2022). The possibility of improving automated calculation of measures of lexical richness for EFL writing: A comparison of the LCA, NLTK, and SpaCy tools. System, 106, 770-786. https://doi.org/10.1016/j.system.2022.102770



--3. </rater_p>--
This is a script that takes the measurements from "spacy_full.py" (as of June 1st, 2022) and uses them to assign grades betweeen 1-4 to paragraphs based on
langauge use alone. It is meant to be used in conjunction with a human rater, as outlined in forthcoming work. The model that this program is trained on is
based on data taken from a single Japanese university, so we recommend creating your own model based on your own student data if you wish to use this at
your own institution. For help doing this, please contact Ryan Spring.

Citations:
Coming soon.

--4. </source_checker>--
This is a script that takes a single "source text" as input and then compares a number of other texts to see how many 3~7 grams are repeated in the sample
texts from the source text. This is a component of </rater_s>.

--5. </rater_s>--
This is a script that takes measurements from "spacy_full.py" and also "source_checker" (see No.4, above) (as of June 1st, 2022). It then uses this data to
assign grades between 0-3 to paragraphs based on language use alone. It is meant to be used in conjunction with a human rater, as outlined in forthcoming work.
The model that this program is trained on is based on data taken from a single Japanese university, so we recommend creating your own model based on your 
own student data if you with to use this at your own institution. For help doing this, please contact Ryan Spring
