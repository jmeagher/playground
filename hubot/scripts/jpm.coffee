
module.exports = (robot) ->

#   robot.hear /jpm/i, (res) ->
#     res.send "JPM says hi!"
#

  robot.brain.data.jpm_faq = questions: {}

  robot.hear /^faqadd ([^ ]*) (.*)/i, (res) ->
    faqName = res.match[1]
    faqContents = res.match[2]
    res.send "Adding new FAQ, question: '#{faqName}' contents: '#{faqContents}'"
    robot.brain.data.jpm_faq.questions[faqName] = faqContents

  robot.hear /^faq$/, (res) ->
    res.send("here are the questions that have been asked so far: #{Object.keys(robot.brain.data.jpm_faq.questions)}")
    res.send(Object.keys(robot.brain.data.jpm_faq.questions).join("\n"))

  robot.hear /^faq ([^ ]*)/i, (res) ->
    faq = res.match[1]
    res.send "question: '#{faq}'  answer:'#{robot.brain.data.jpm_faq.questions[faq]}'"

