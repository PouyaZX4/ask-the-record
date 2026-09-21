import {defineField, defineType} from 'sanity'

export const article = defineType({
  name: 'article',
  title: 'Article',
  type: 'document',
  fields: [
    defineField({
      name: 'foremId',
      title: 'Forem ID',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'slug',
      title: 'Slug',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'url',
      title: 'URL',
      type: 'url',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'title',
      title: 'Title',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'publishedAt',
      title: 'Published at',
      type: 'datetime',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'editedAt',
      title: 'Edited at',
      type: 'datetime',
    }),
    defineField({
      name: 'body',
      title: 'Body (markdown)',
      type: 'text',
      rows: 20,
      description: 'Full published markdown from Forem. This is what a Knowledge Base indexes; without it the KB sees only a title.',
    }),
    defineField({
      name: 'retractionParagraph',
      title: 'Retraction paragraph',
      type: 'text',
      rows: 4,
      description: 'The public correction text. Must live on the article, not only as a claim, or a Knowledge Base built from articles cannot quote it.',
    }),
    defineField({
      name: 'status',
      title: 'Status',
      type: 'string',
      options: {
        list: [
          {title: 'Live', value: 'live'},
          {title: 'Retracted in place', value: 'retracted-in-place'},
          {title: '404', value: '404'},
        ],
        layout: 'radio',
      },
      initialValue: 'live',
      validation: (Rule) => Rule.required(),
    }),
  ],
  preview: {
    select: {title: 'title', subtitle: 'status'},
  },
})
